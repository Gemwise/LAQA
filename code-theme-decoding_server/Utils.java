import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Utils {
    // handle tiles map
    public static HashMap<Integer, String> id2pose = new HashMap<> ();

    public static HashMap<Integer, String> id2addr = new HashMap<> ();
    public static HashMap<String, Integer> pose2id = new HashMap<> ();
    public static HashMap<Integer, Integer> id2size = new HashMap<> ();
    public static HashMap<Integer, byte[]> map = new HashMap<> ();
    public static HashMap<String, ArrayList<Integer>> predTileTable = new HashMap<> ();
    public static HashMap<String, ArrayList<Integer>> reqTileTable = new HashMap<> ();

    // locate the statistics for each client by IP
    public static HashMap<String, Stats> clientStats = new HashMap<> ();

    // handler the general statistics
    public static volatile String curPos = null;
    public static volatile String[] predPos = null;
    public static HashMap<Integer, String> realPoses = new HashMap<> ();
    public static String teacherAddr = null; //"/192.168.1.6";//"/172.20.241.88";
    //public static boolean netStartFlag = false; // triggered by the first received teacher's trace
    public static boolean netEndFlag = false; // triggered by the teacher's last trace
    public static float granular = 5f;
    public static int traceSendInterval = 3;
    public static int tilesNum = 0;

    //1080p --- quality
    public final static int qualityLevel = 6;
    public final static int[] availQuality = {15, 19, 23, 27, 31, 35};

    // map quality  15，19,23,27,31,35 --> 6,5,4,3,2,1   (crf->quality)
    public final static HashMap<Integer, Integer> qualityMap = new HashMap<> () {{
        put (15, 6);
        put (19, 5);
        put (23, 4);
        put (27, 3);
        put (31, 2);
        put (35, 1);
    }};

    public final static HashMap<Integer, Float> decodeTimeMap = new HashMap<> () {{
        put (6,16.75F);
        put (5,17.43F);
        put (4,17.45F);
        put (3,17.54F);
        put (2,17.58F);
        put (1,18.01F);
    }};

//2k --- quality
 /*public final static int qualityLevel = 8;
	public final static int[] availQuality = {15,17,18,22,26,31,35,39};
// map quality from 15,17,18,22,26,31,35,39 to 8, 7,6,5,4,3,2,1  (crf->quality)
public final static HashMap<Integer, Integer> qualityMap = new HashMap<> () {{
    put (15, 8);
    put (17, 7);
    put (18, 6);
    put (22, 5);
    put (26, 4);
    put (31, 3);
    put (35, 2);
    put (39, 1);
}};

    public final static HashMap<Integer, Float> decodeTimeMap = new HashMap<> () {{
        put (8,16.49F);
        put (7,16.88F);
        put (6,17.01F);
        put (5,17.13F);
        put (4,17.18F);
        put (3,17.64F);
        put (2,17.83F);
        put (1,18.54F);
    }};
*/
    
/*
//4k --- quality
	public final static int qualityLevel = 10;
	public final static int[] availQuality = {15,17,19,21,23,27,32,37,41,45};
// map quality from 15,17,19,21,23,27,32,37,41,45 to 10,9,8,7,6,5,4,3,2,1
public final static HashMap<Integer, Integer> qualityMap = new HashMap<> () {{
    put (15, 10);
    put (17, 9);
    put (19, 8);
    put (21, 7);
    put (23, 6);
    put (27, 5);
    put (32, 4);
    put (37, 3);
    put (41, 2);
    put (45, 1);
}};

    public final static HashMap<Integer, Float> decodeTimeMap = new HashMap<> () {{
        put (10, 16.72F);
        put (9,16.76F);
        put (8,16.78F);
        put (7,17.19F);
        put (6,17.14F);
        put (5,17.38F);
        put (4,18.23F);
        put (3,18.61F);
        put (2,19.06F);
        put (1,20.18F);
    }};*/
    
    public static int timeSlot = 0;
    public static int TARGET_FPS = 60;
    public static int FRAME_PERIOD = 1000 / Utils.TARGET_FPS - 1; // Frame period of the video to stream, in ms

    // port forwarding 
    public final static HashMap<String, Integer> portForward = new HashMap<> () {{
        put ("192.168.1.6", 65506);
        put ("192.168.1.10", 65510);
        put ("192.168.1.13", 65513);
        put ("192.168.1.9", 65509);
        put ("192.168.1.11", 65511);
        put ("192.168.1.15", 65515);
        put ("192.168.1.16", 65516);
        put ("192.168.1.17", 65517);
        put ("192.168.1.19", 65519);
    }};

    // statistics to optimization
    public static float ALPHA = 0.1f; //trans_time:author-> 0.1f,our->  0.1f
    public static float BETA = 0.5f; //var_portion :author-> 0.5f ,our-> 0.5f
    public static float GAMMA = 0.05f; //decode_time: author -> no,our-> 0.05f
    public static float RATE_LIMIT_SERVER = 800f ; // unit: MB/s
//    public static float RATE_LIMIT_SERVER = Float.POSITIVE_INFINITY;
    public final static int[] RATE_LIMIT_GUIDELINES = {40,45,50,55,60};   //原作unit: Mbps

    public enum Algorithm {
        Firefly,
        TwoApprox,
        PAVQ,
        LAQA_FairnessCom
    }

    public static Algorithm policy = Algorithm.LAQA_FairnessCom;

    // given the throughput limitation
/*    public final static HashMap<String, Float> throughputMap = new HashMap<> () {{
        put ("/192.168.1.6", 40 / 8f);
        put ("/192.168.1.10", 20 / 8f);
        put ("/192.168.1.13", 60 / 8f);
        put ("/192.168.1.9", 75 / 8f);
        put ("/192.168.1.11", 50 / 8f);
    }};*/
    
    final static boolean our_method = true;
    final static boolean our_method_fairnee = true;
    

    public final static HashMap<String, Boolean> clientComputationMap = new HashMap<>(){{

        put("192.168.50.135", false);
        put("192.168.50.164", false);
        put("192.168.50.250", false);

        put("192.168.50.134", true);
        put("192.168.50.42", true);
        put("192.168.50.181", true);

    }};
    // probability estimation
    public static float estProb = 1;

    // handle the problems met during transmission
    // if have pose, cannot find id, the pose will be stored in this array
    // if have id, cannot find frame, the video id will be stored in this array
    public static ArrayList<String> notFoundFrames = new ArrayList<> ();

    public static float calBandwidth (String indexPos, ArrayList<Integer> tiles, int quality) {
        quality = Utils.getCRF (quality); //convert from quality level to CRF
        int totalSize = 0;
        for (int tile_id : tiles) {
            int videoID = Utils.getVideoID (indexPos, tile_id, quality);
            if (Utils.id2size.containsKey (videoID))
                totalSize += Utils.id2size.get (videoID);   // unit: Byte
        }
        // considering the reservation for decoding
        return (float) totalSize / ((Utils.FRAME_PERIOD) * 1000); // unit: MB/s
        // totalSize/1000*1000  :Byte->M Byte
        // Utils.FRAME_PERIOD / 1000  :ms->s
        // (totalSize/1000*1000)/(Utils.FRAME_PERIOD / 1000)=totalSize / ((Utils.FRAME_PERIOD) * 1000) unit: MB/s
    }

    public static int getCRF (int qualityLevel) {
        return Utils.availQuality[Utils.qualityLevel - qualityLevel];
    }


    public static int getPredResult (String predPose, String realPose, int flag) {

        int result = 1;
        
        int quality = 15;
        // get requested tiles use real pose
        ArrayList<Integer> requestTiles = new ArrayList<> ();
        String indexPos = Utils.getPosIndex (realPose);  // pos,
        float[] ori = Utils.getOri (realPose);         //ori
        String coor = "(" + (int) Utils.calAngle (ori[0]) + "," + (int) Utils.calAngle (ori[1]) + "," + 0 + ")";
        ArrayList<Integer> tiles = Utils.reqTileTable.get (coor);
        for (int tile_id : tiles) {
            int videoID = Utils.getVideoID (indexPos, tile_id, quality);
            requestTiles.add (videoID);
        }

        // get transmitted tiles use predicted pose
        ArrayList<Integer> transTiles = new ArrayList<> ();
        indexPos = Utils.getPosIndex (predPose);
        ori = Utils.getOri (predPose);
        coor = "(" + (int) Utils.calAngle (ori[0]) + "," + (int) Utils.calAngle (ori[1]) + "," + 0 + ")";

        if (flag == 1) {// for transmission
            tiles = Utils.predTileTable.get (coor);
        } else if (flag == 0) {// for display validation
            tiles = Utils.reqTileTable.get (coor);
        }

        for (int tile_id : tiles) {
            int videoID = Utils.getVideoID (indexPos, tile_id, quality);
            transTiles.add (videoID);
        }

        //detect whether all requested tiles are transmitted
        for (int tileID : requestTiles) {
            if (!transTiles.contains (tileID)) {
                result = 0;
                break;
            }
        }
        return result;
    }

    public static int getVideoID (String indexPos, int tileID, int quality) {
        String pose = indexPos + "," + tileID + "," + quality;
        if (!Utils.pose2id.containsKey (pose)) {
            Utils.notFoundFrames.add (pose);
            return -1;
        }
        int videoID = Utils.pose2id.get (pose);
        return videoID;
    }

    public static double calPos (double pos, float granularity) {
        return (int) (pos / granularity) * granularity;
    }

    public static String getPosIndex (String recvStr) {
        String[] posStr = null;
        if (recvStr.contains (","))
            posStr = recvStr.split (",");
        else {
            posStr = recvStr.split (" ");
        }
        double[] positions = new double[2];
        for (int i = 0; i < 2; i++) {
            positions[i] = calPos (Float.parseFloat (posStr[i]), granular);
        }
        //String posX = recvStr.substring(0,recvStr.indexOf(",")).trim();
        //String posY = recvStr.substring(recvStr.indexOf(",")+1).trim();
        String pos = (int) positions[0] + "," + (int) positions[1];
        return pos;
    }

    public static float calAngle (float degree) {
        float result = (degree + 180.f) % 360.f - 180.f;
        return result < -180 ? result + 360.f : result;
    }

    public static float[] getPos (String recvStr) {
        String[] posStr = null;
        if (recvStr.contains (","))
            posStr = recvStr.split (",");
        else {
            posStr = recvStr.split (" ");
        }
        float[] positions = new float[2];

        for (int i = 0; i < 2; i++) {
            positions[i] = Float.parseFloat (posStr[i]);
        }

        return positions;
    }

    public static float[] getOri (String recvStr) {
        String[] coor = recvStr.split (" ");
        float[] orientations = new float[2];
        for (int i = 0; i < 2; i++) {
            orientations[i] = Float.parseFloat (coor[i + 2]);
        }
        return orientations;
    }
}