import com.sun.management.OperatingSystemMXBean;

import java.lang.Thread;
import java.lang.management.ManagementFactory;
import java.net.*;
import java.io.*;
import java.time.Instant;
import java.util.*;

public class PredictThread extends Thread {

    BufferedReader input;
    Socket socket;
    int histWind;
    int predWind;
    int msgLen;
    //boolean startFlag = true;
    String lastPose = null;
    LRModelWrap lrWrapPosX;
    LRModelWrap lrWrapPosZ;
    LRModelWrap lrWrapOriX;
    LRModelWrap lrWrapOriY;
    RateAlgo algo;
    //String curPos;

    PredictThread (String name, Socket sock, BufferedReader prereader) {
        super (name);
        socket = sock;
        histWind = 3;
        predWind = 1;
        lrWrapPosX = new LRModelWrap (predWind, histWind);
        lrWrapPosZ = new LRModelWrap (predWind, histWind);
        lrWrapOriX = new LRModelWrap (predWind, histWind);
        lrWrapOriY = new LRModelWrap (predWind, histWind);
        input = prereader;
    }

    @Override
    public void run () {
        try {
            // initialize the rate control algorithm based on policy
            switch (Utils.policy) {
                case Firefly:
                    System.out.println("Using Algorithm: Firefly");
                    algo = new Firefly ();
                    break;
                case TwoApprox:
                    System.out.println("Using Algorithm: TwoApprox");
                    algo = new TwoApprox ();
                    break;
                case PAVQ:
                    System.out.println("Using Algorithm: PAVQ");
                    algo = new PAVQ ();
                    break;
                case LAQA_FairnessCom:
                    System.out.println("Using Algorithm: LAQA_FairnessWithCom");
                    algo = new LAQA_FairnessWithCom ();
                    algo.classifyClient();
                    break;
                default:
                    System.out.println("Unknown algorithm");
                    break;
            }

            System.out.println (Thread.currentThread ().getName () + " Start receiving the trace");
            String line = input.readLine ();// receive the first trace from the teacher

            while (line != null) {
//                long t1 = System.currentTimeMillis ();
//                System.out.println ("current slot: " + (Utils.timeSlot + 1));
 
                Utils.curPos = line;

                if (lastPose != null) {
                    int result = Utils.getPredResult (lastPose, Utils.curPos, 1);
                    Utils.estProb = (result + Utils.timeSlot * Utils.estProb) / (Utils.timeSlot + 1);
                }

                // motion prediction
                float[] positions = Utils.getPos (line);
                float[] orientations = Utils.getOri (line);

                double posX = positions[0];
                double[] predPosXs = lrWrapPosX.step (posX);
                double posZ = positions[1];
                double[] predPosZs = lrWrapPosZ.step (posZ);
                double oriX = orientations[0];
                double[] predOriXs = lrWrapOriX.step (oriX);
                double oriY = orientations[1];
                double[] predOriYs = lrWrapOriY.step (oriY);

                String[] predLines = new String[predWind];
                for (int i = 0; i < predWind; i++) {
                    double predPosX = predPosXs[i];
                    double predPosZ = predPosZs[i];
                    double predOriX = predOriXs[i];

                    if (predOriX > 90) {
                        predOriX = 90;
                    } else if (predOriX < -90) {
                        predOriX = -90;
                    }
                    double predOriY = predOriYs[i];
                    String predLine = predPosX + " " + predPosZ + " " + predOriX + " " + predOriY;
                    predLines[i] = predLine;
                }

                Utils.predPos = predLines;
                lastPose = predLines[0];
                
                algo.allocate (); //policy rate control

                Utils.realPoses.put (Utils.timeSlot, line);
                Utils.timeSlot++;

               /* long t2 = System.currentTimeMillis ();
                long timePast = t2 - t1;
                System.out.println (Thread.currentThread ().getName () + " Predict Time done: " + timePast);*/

                line = input.readLine ();
            }

            System.out.println (Thread.currentThread ().getName () + " Trace recive done");
            input.close (); // will close all underlying stream
            Utils.netEndFlag = true;
        } catch (IOException e) {
            e.printStackTrace ();
        }

    }

}