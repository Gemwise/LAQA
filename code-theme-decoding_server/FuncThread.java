import java.lang.Thread;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.net.*;
import java.io.*;
import java.util.*;


public class FuncThread extends Thread {
    private Socket socket;
    private String clientAddr;
    BufferedReader reader;
    //private Stats curStat;
    private FileWriter fwt;
    private String filename;
    private double oneWayDelayNoData;
    private int ackSize;
    private int clientNum;
    private Timer timer;

    private ArrayList<Integer> videoACKReport;
    private ArrayList<Integer> timeACKReport;
    private HashMap<Integer, Float> delayACKReport;
    private HashMap<Integer, Float> throughputReport;
    private ArrayList<String> poseACKReport;
    private ArrayList<Float> varQualityReport;

    Stats statistics = null;

    public FuncThread (String name, Socket sock, String IP, BufferedReader prereader) {
        // get the name of the thread
        super (name);

        socket = sock;
        clientAddr = IP;

        statistics = Utils.clientStats.get (clientAddr);
        clientNum = statistics.clientNum;
        oneWayDelayNoData = 0.0;
        ackSize = ACKpacket.HEADER_SIZE;
        videoACKReport = new ArrayList<> ();
        timeACKReport = new ArrayList<> ();
        poseACKReport = new ArrayList<> ();
        delayACKReport = new HashMap<> ();
        throughputReport = new HashMap<> ();
        varQualityReport = new ArrayList<> ();

        reader = prereader;
    }

    private void reportStats () {

        System.out.println (Thread.currentThread ().getName () + " start writing the functional report");
        String fileName = null;
        
        try {
            if (clientAddr.equals (Utils.teacherAddr)) {
                fileName = Utils.policy + "_teacher_" + clientAddr + ".txt";
                System.out.println ("estimated prediction probability: " + String.format("%.2f", Utils.estProb));
            } else {
                fileName = Utils.policy + "_student_" + clientAddr + ".txt";
            }
            String path = "report";
            File folder = new File (path);
            if (!folder.exists ()) {
                System.out.print ("No Folder");
                folder.mkdir ();
                System.out.print ("Folder created");
            }
//            System.out.println ("create report directory");
            File file = new File ("./report/" + fileName);
            file.createNewFile ();
            System.out.println ("create ./report/"+ fileName);
            FileWriter fwt = new FileWriter (file);
//            fwt.write ("slot, allocate quality, display quality, pose, delay, throughput, video size, varQuality\n");
//            fwt.write ("slot, allocate quality, display quality,delay,varQuality,throughput,pose\n");
            for (int i = 0; i < videoACKReport.size (); i++) {
                int slot = timeACKReport.get (i);
                //1. ABR algorithm quality
                int targetQuality = -1;
                if (statistics.videoQualitySlot.containsKey (slot)) {
                    targetQuality = statistics.videoQualitySlot.get (slot);
                }
                //2. client ack quality
                int quality = 0;
                quality = videoACKReport.get (i);
                //3. transmit delay
                float delay = 0;
                if (delayACKReport.containsKey (slot)) {
                    delay = delayACKReport.get (slot);
                }
                //4.throughput  real-time
                float throughput = 0;
                if (throughputReport.containsKey (slot)) {
                    throughput = throughputReport.get (slot);
                }
                //5.videoSize : totalTileSize
                int videoSize = 0;
                if (statistics.videoSizeSlot.containsKey (slot)) {
                    videoSize = statistics.videoSizeSlot.get (slot);
                }
                //6.pose
                String pose = poseACKReport.get (i);
                //7.varQuality
                float varQuality = 0;
                varQuality = varQualityReport.get (i);
                BigDecimal bd = new BigDecimal(varQuality);
                bd = bd.setScale(2, RoundingMode.HALF_UP);
                varQuality = bd.floatValue();
                
//                fwt.write (slot + "," + targetQuality + "," + quality + "," + pose + "," + delay + "," + throughput + "," + videoSize + "," + varQuality + "\n");
                fwt.write (slot + "," + targetQuality + "," + quality + "," + delay + "," + varQuality + "," + throughput + "," + videoSize + "\n");
                fwt.flush ();
            }

            fwt.close ();

        } catch (IOException e) {
            e.printStackTrace ();
        }
        System.out.println ("estimated throughput: " + String.format("%.2f",statistics.estThroughput) + " MB/s");
        System.out.println (Thread.currentThread ().getName () + ": Report of " + fileName + " has been done");

    }

    @Override
    public void run () {
        System.out.println (Thread.currentThread ().getName () + " New client connected, from: " + clientAddr);

        try {
            socket.setTcpNoDelay (true);
            
            while (socket != null && !Utils.netEndFlag) {

                //byte[] ackBytes = new byte[ackSize];
                // Receive displayed ACK or packet ACK from the client
                //input.read(ackBytes);
                String ackLine = reader.readLine ();
                long t = System.currentTimeMillis ();

                //ACKpacket ack = new ACKpacket(ackBytes,ackSize);
                String[] tokens = null;
                if (ackLine.contains (",")) {
                    tokens = ackLine.split (",");
                } else {
                    tokens = ackLine.split (" ");
                }
                int ackType = Integer.parseInt (tokens[0]);
                if (ackType == 0) {
                    // display ACK 
                    int videoID = Integer.parseInt (tokens[1]);
                    int slot = Integer.parseInt (tokens[2]);
                    String pose = null;
                    int quality = 0;
                    if (videoID != -1) {
                        quality = Integer.parseInt (Utils.id2pose.get (videoID).split (",")[3]);
                        quality = Utils.qualityMap.get (quality); //convert from CRF to quality
                        float oriX = Float.parseFloat (tokens[3]);
                        float oriY = Float.parseFloat (tokens[4]);
                        String posX = Utils.id2pose.get (videoID).split (",")[0];
                        String posZ = Utils.id2pose.get (videoID).split (",")[1];
                        pose = posX + " " + posZ + " " + oriX + " " + oriY;

                        // double check for students, since they do not know the prediction result
                        if (!clientAddr.equals (Utils.teacherAddr) && Utils.realPoses.containsKey (slot)) {
                            String realPose = Utils.realPoses.get (slot);
                            int result = Utils.getPredResult (pose, realPose,0);
                            if (result == 0) {
                                System.out.println ("clientAddr getPredResult xxx");
                                quality = 0;
                            }
                        }
                    }
                    else
                    {
                        System.out.println ("send display ACK with videoID -1 to show missed frame");
                    }
                    // calculate mean and variance of display quality
                    statistics.varQuality = (float) ((slot - 1) * statistics.varQuality / slot + Math.pow (quality - statistics.aveQuality, 2) / (slot + 1));
                    statistics.aveQuality = (quality + slot * statistics.aveQuality) / (slot + 1);

                    poseACKReport.add ("(" + pose + ")");
                    videoACKReport.add (quality);
                    timeACKReport.add (slot);
                    varQualityReport.add (statistics.varQuality);

                } else if (ackType == 1) {
                    // packet ACK, refer to a tile is successfully received
                    int videoID = Integer.parseInt (tokens[1]);
                    int slot = Integer.parseInt (tokens[2]);
                    int endTile = Integer.parseInt (tokens[3]);
                    
                    if (endTile == 1) {
                        // all tiles in this time slot have been ACked
                        statistics.calDelayEndTime = System.nanoTime ();
                        float delay = Float.parseFloat (tokens[4]); //unit: ms
                        BigDecimal bd = new BigDecimal(delay);
                        bd = bd.setScale(2, RoundingMode.HALF_UP);
                        delay = bd.floatValue();

                        //polynomia regression to predict delay
                        // ignore invalid delay
                        if (delay > 0 && delay < 100 && statistics.videoSizeSlot.containsKey (slot)) {
                            int size = statistics.videoSizeSlot.get (slot);
                            float rate = (float) size / (Utils.FRAME_PERIOD * 1000); // unit: MB/s
                            statistics.fitDelay (rate, delay);  //polynomia regression
                            //System.out.println(Thread.currentThread().getName()+" add delay: "+delay);
                        }
                        delayACKReport.put (slot, delay);
                        //System.out.println(Thread.currentThread().getName()+" receive delay "+delay+" in time slot :"+slot );

                        //To use the Exponential Moving Average (EMA) algorithm in code to estimate available bandwidth
                        float estThroughput = Float.parseFloat (tokens[5]);
                        BigDecimal bd_estThroughput = new BigDecimal(estThroughput);
                        bd_estThroughput = bd_estThroughput.setScale(2, RoundingMode.HALF_UP);
                        estThroughput = bd_estThroughput.floatValue();
                        // throughput estimation
                        if (estThroughput > 0) {
//                            statistics.estThroughput = statistics.expFactor * estThroughput  +  (1 - statistics.expFactor) * statistics.estThroughput;
                            //modify
                            statistics.estThroughput = statistics.expFactor * statistics.estThroughput  +  (1 - statistics.expFactor) * estThroughput;
                        }
                        throughputReport.put (slot, estThroughput);
                    }

                    statistics.prevPose.add (videoID);
                    //System.out.println(Thread.currentThread().getName()+" receive packet ACK of videoID :"+videoID );
                } else if (ackType == 2) {
                    // video release ACK
                    int videoID = Integer.parseInt (tokens[1]);
                    if (statistics.prevPose.contains (videoID))
                        statistics.prevPose.remove (videoID);
                    //System.out.println(Thread.currentThread().getName()+" release video: "+videoID);
                }
            }
            System.out.println("**************************************");
            Utils.netEndFlag = true; // triggered multiple times
            reader.close (); // will close all underlying stream
            System.out.println (Thread.currentThread ().getName () + ": client from: " + clientAddr + " has been closed.");
        } catch (IOException e) {
            System.out.println (Thread.currentThread ().getName () + " exception: " + e.getMessage ());
            e.printStackTrace ();
        } finally {
            System.out.println ("start try-finally:");
            reportStats ();
        }
    }
}

