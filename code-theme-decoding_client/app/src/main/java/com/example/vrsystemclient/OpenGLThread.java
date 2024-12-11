package com.example.vrsystemclient;

import android.content.Context;
import android.graphics.SurfaceTexture;
import android.opengl.GLES30;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Message;
import android.util.Log;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.Timer;
import java.util.TimerTask;


public class OpenGLThread extends HandlerThread {
    public Handler handler;

    private int nDecoders;
    private static SurfaceTexture displaySurfaceTexture;
    private Context context;
    private Timer displayTimer;


    private static boolean setupdelay = true;
    // clocking thread pause/resume variables
    private static Object mPauseLock;
    private static boolean mPaused;
    private static boolean mFinished;

    /**
     * 代码的意思是任务会在初始延迟 sleepInterval*2 后第一次执行，然后每隔 sleepInterval 执行一次。
     * 每次执行时，它会自增 Utils.timeSlot 并调用 handler.sendEmptyMessage(Config.MSG_FRAME_SYNC)。
     * */
    void setTimer(){
        displayTimer = new Timer();
        int sleepInterval = (int) (1000 / (double) (Config.TARGET_FPS) - 1);
        // wait for receiving the first RTP packet
        while (!Utils.startDisplay){
            try {
//                System.out.println("Waiting");
                Thread.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        //第一个参数 sleepInterval*2 是初始延迟时间（任务首次执行前的等待时间），
        // 第二个参数 sleepInterval 是任务的周期时间（两次执行之间的间隔）
        displayTimer.schedule(new TimerTask() {
            @Override
            public void run() {
                Utils.timeSlot++;
                handler.sendEmptyMessage(Config.MSG_FRAME_SYNC);
            }

        }, sleepInterval*2, sleepInterval);
    }

    public OpenGLThread(String name, int nDecoders, SurfaceTexture surfaceTexture, Context context) {
        super(name);
        this.nDecoders = nDecoders;
        this.context = context;
        displaySurfaceTexture = surfaceTexture;
    }

    //同步锁可有可无 目前10.23
    private static synchronized void updateDisplay() {
        // clear display surface texture
        GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT);

        // draw tiles
        String frame = System.currentTimeMillis() + " ";
        for(int videoID : Utils.displayVideoIDs) {
            FrameCache.drawSingleTile(videoID, displaySurfaceTexture, Config.COLOR);
            Stats.tileDispd.add(videoID);
            frame += (videoID + " ");
        }
        Stats.frameDisp.add(frame);

        sendDispACK(Utils.displayVideoIDs.get(0)); // 只发送第一个videoid

        // display what have been drawn
        OpenGLHelper.display();

        // update camera matrix according to sensor reading
        OpenGLHelper.updateCamera();

        // calculate FPS
        if(Stats.nDisplayed == 0) {
            Stats.startTS = System.currentTimeMillis();
        }
        Stats.nDisplayed++;
        if(Stats.nDisplayed == Config.FPS_CAL_INTERVAL) {
            float thisFPS = 1000.0f/((float)(System.currentTimeMillis() - Stats.startTS)/(Config.FPS_CAL_INTERVAL - 1));
            BigDecimal  bd = BigDecimal.valueOf(thisFPS).setScale(2, RoundingMode.HALF_UP); //保留2位小数
            double fpsRoundedValue = bd.doubleValue();
            Stats.FPSs.add(System.currentTimeMillis() + " " + fpsRoundedValue);
            Stats.nDisplayed = 0;
            Log.i(Config.GLOBAL_TAG, "thisFPS = " + thisFPS);
            MainActivity.connText.setText("FPS: "+(int)thisFPS);
        }

        Stats.nTotalDisplayed++;
    }

    private static void sendDispACK(int videoID) {
        // let the functional thread send the display ack, only send one ACK each slot
        Message msg = MainActivity.funcNet.handler.obtainMessage(Config.SEND_DISP_ACK);
        Bundle bundle = new Bundle();
        bundle.putString(Config.MSG_KEY, 0 +","+videoID+","+Utils.timeSlot+","+Utils.coorX+","+Utils.coorY);
        msg.setData(bundle);
        MainActivity.funcNet.handler.sendMessage(msg);
    }


    /** Entry point. */
    public void start() {
        super.start();

        handler = new Handler(getLooper()) {
            @Override
            public void handleMessage(Message msg) {
                switch (msg.what) {
                    case Config.MSG_SETUP: {
                        // init opengl
                        OpenGLHelper.oneTimeSetup(displaySurfaceTexture);

                        // init frameCache (surfaceTextures, surfaces, extTextures, myGLTextures...)
                        FrameCache.init(Config.FBO_CACHE_SIZE, nDecoders);

                        // init template header for decoding
                        Utils.initMegaTemplate();

                        // start decoders
                        Utils.mFrameDecoders = new FrameDecoder[nDecoders];
                        for(int i = 0; i < nDecoders; i++) {
                            Utils.mFrameDecoders[i] = new FrameDecoder(i); // one decoding thread instance
                            FrameDecoderWrapper.runExtractor(Utils.mFrameDecoders[i]);
                        }

                        // connect to server, request initial list (step 0)
                        Utils.naviIdx = 0;

                        // start clock thread to fire MSG_FRAME_SYNC every 1/FPS second
                        //没有用到
                        mPauseLock = new Object();
                        mPaused = false;
                        mFinished = false;

                        //new Thread(new ClockThread(handler)).start();
                        setTimer();
                        break;
                    }
                    case Config.MSG_ON_FRAME_AVAILABLE: {
                        int decoderID = msg.arg1;
                        int videoID = Utils.mFrameDecoders[decoderID].videoID;
                        //System.out.println("video id: "+videoID+" has been decoded, send to frame buffer");

                        if(videoID < 0) throw new RuntimeException("MSG_ON_FRAME_AVAILABLE error");

                        // latch the data
                        FrameCache.mSurfaceTextures[decoderID].updateTexImage();
                        // cache to FBO, upper half is color lower half is depth
                        FrameCache.cache2FBO(videoID, FrameCache.mSurfaceTextures[decoderID], FrameCache.extTextures[decoderID]);
                        // release decoder awaitNewImage() lock
                        Utils.mFrameDecoders[decoderID].bFrameCached = true;

                        break;
                    }
                    case Config.MSG_FRAME_SYNC: {
                        // check if current visible tiles are cached in FBO
                        Utils.updateDisplayPose();
                        Utils.displayVideoIDs = Utils.getCurVisibleTiles();

                        if(!FrameCache.FBOcacheContainsCurVisibleTiles()) {
                            Log.e(Config.GLOBAL_TAG, "FATAL: tiles not available for step " + Utils.naviIdx);
                            Stats.missedStep.add(Utils.naviIdx);
                            if(Stats.lastMissTS != 0)
                                Stats.totalStall += System.currentTimeMillis() - Stats.lastMissTS;
                            Stats.lastMissTS = System.currentTimeMillis();
                            // per trace idx num of stalls
                            if(Stats.traceIdxStalls.containsKey(Utils.naviIdx))
                                Stats.traceIdxStalls.put(Utils.naviIdx, Stats.traceIdxStalls.get(Utils.naviIdx) + 1);
                            else
                                Stats.traceIdxStalls.put(Utils.naviIdx, 1);

                            // send display ACK with videoID -1 to show missed frame
                            sendDispACK(-1);
                        } else {
                            Stats.lastMissTS = 0;
                            //Utils.dispBuffer.remove(0);
                            //System.out.println("pose to display: "+Utils.naviPos + "," + Utils.coorX + "," + Utils.coorY);
                            // update display
                            updateDisplay();
                        }

                        break;
                    }

                    case Config.MSG_REPORT_STATUS: {
                        // ClockThread.pause();
                        displayTimer.purge();
                        displayTimer.cancel();
                        reportStats();
                        break;
                    }

                    default: {
                        Log.e(Config.GLOBAL_TAG, "handler thread receive unknown msg");
                        break;
                    }
                }
            }
        };
    }

    private static void reportStats(){
        Log.e(Config.GLOBAL_TAG, "Statistics report start.");

        File reportFile = new File(
                MainActivity.rootDir,
                "fps.csv");
        File decodeTimeFile = new File(
                MainActivity.rootDir,
                "latency.csv");
        try {
            reportFile.createNewFile();
            FileWriter reportFwt = new FileWriter(reportFile);
            for(String item : Stats.FPSs) {
                float fps = Float.parseFloat(item.split(" ")[1]);
//                if (fps > 65.0f) fps = 65.0f;
                // fw.write(item.split(" ")[0] + " " + fps + "\n");
                reportFwt.write(fps + ",\n");
            }
            reportFwt.flush();
            reportFwt.close();

            decodeTimeFile.createNewFile();
            FileWriter decodewt = new FileWriter(decodeTimeFile);
//            decodewt.write("quality"+","+"ts"+",\n");
            for (Stats.valueOfdecodeTime item : Stats.decodeTime){
                Long latency = item.ts;
                int quality = item.quality;
//                String videoid = item.videoID;
//                decodewt.write(videoid+','+String.valueOf(quality) +','+ts.toString()+",\n");
                decodewt.write(String.valueOf(quality) +','+ latency.toString()+",\n");
            }
            decodewt.flush();
            decodewt.close();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}
