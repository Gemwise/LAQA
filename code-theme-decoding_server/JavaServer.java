import java.io.*;
import java.net.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.nio.file.Files;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.io.*;
import java.nio.file.*;

/**
 * This program demonstrates a simple TCP/IP socket server that echoes every
 * message from the client in reversed form.
 * This server is single-threaded.
 */
public class JavaServer {

    static void prepareBuffer (String folderName) {
        File folder = new File (folderName);
        File[] listOfFiles = folder.listFiles ();
        int filenum = 0;
        long startPrepTime = System.currentTimeMillis ();
        for (File f : listOfFiles) {
            String fileName = f.getName ();
            byte[] curFrame = null;
            try {
                curFrame = Files.readAllBytes (f.toPath ());
            } catch (IOException e) {
                System.out.println ("Main thread: Frame Buffer exception: " + e.getMessage ());
                e.printStackTrace ();
            }
            String pos = fileName.substring (fileName.indexOf ("(") + 1, fileName.indexOf (")"));
            int tileID = Integer.parseInt (fileName.substring (fileName.indexOf ("tile") + 4, fileName.indexOf ("crf")));
            int crf = Integer.parseInt (fileName.substring (fileName.indexOf ("crf") + 3, fileName.indexOf (".264")));
            int videoID = Utils.getVideoID (pos, tileID, crf);
            if (videoID != -1) {
                Utils.map.put (videoID, curFrame);
                Utils.id2size.put (videoID, curFrame.length);
            }
            long curTime = System.currentTimeMillis ();
            if (filenum % 1000 == 0)
                System.out.println ("read " + filenum + " files, time used: " + (curTime - startPrepTime) + " ms");
            filenum++;
        }
        // save the id2size table
        /*File file = new File("./id2size.txt");
        try {
			BufferedWriter bw = new BufferedWriter(new FileWriter(file));
			for(int videoID : Utils.id2size.keySet()) {
				bw.write(videoID + "," + Utils.id2size.get(videoID) + "\n");
			}
			bw.close();
		} catch (IOException e) {
			e.printStackTrace();
		}*/

        if (!Utils.notFoundFrames.isEmpty ()) {
            for (int i = 0; i < Utils.notFoundFrames.size (); i++) {
                System.out.println ("Main thread: cannot find id of the pose: " + Utils.notFoundFrames.get (i));
            }
        }
        System.out.println ("Buffer Ready");
    }

    static void readIDTable (String filename, HashMap<Integer, String> id2pose, HashMap<String, Integer> pose2id) {
        File file = new File (filename);
        id2pose.clear ();
        pose2id.clear ();
        try {
            BufferedReader br = new BufferedReader (new FileReader (file));

            String st;
            int cnt = 0;
            while ((st = br.readLine ()) != null) {
                String[] strs = st.split (" ");
                int videoID = Integer.parseInt (strs[0]);
                String pose = strs[1];
                id2pose.put (videoID, pose);
                pose2id.put (pose, videoID);
                cnt++;
            }
            br.close ();
            // print the hashmap
            //System.out.println(table);
            System.out.println ("Tile ID Table read done, total id count:" + cnt);
        } catch (IOException e) {
            e.printStackTrace ();
        }
    }

    public static HashMap<Integer, String> buildVideoIdToPathMap (String folderPath) {
        HashMap<Integer, String> videoIdToPathMap = new HashMap<> ();
        File folder = new File (folderPath);
        File[] listOfFiles = folder.listFiles ();

        for (File f : listOfFiles) {
            String fileName = f.getName ();
            String pos = fileName.substring (fileName.indexOf ("(") + 1, fileName.indexOf (")"));
            int tileID = Integer.parseInt (fileName.substring (fileName.indexOf ("tile") + 4, fileName.indexOf ("crf")));
            int crf = Integer.parseInt (fileName.substring (fileName.indexOf ("crf") + 3, fileName.indexOf (".264")));
            int videoID = Utils.getVideoID (pos, tileID, crf);

            if (videoID != -1) {
                videoIdToPathMap.put (videoID, f.getAbsolutePath ());
                //System.out.println (videoID+"  "+f.getAbsolutePath());
            }
        }
        return videoIdToPathMap;
    }

    static HashMap<String, ArrayList<Integer>> readTileTable (String filename) {
        HashMap<String, ArrayList<Integer>> table = new HashMap<> ();
        File file = new File (filename);
        try {
            BufferedReader br = new BufferedReader (new FileReader (file));

            String st;
            int cnt = 0;
            String coor = null;
            /*(14,-58,0)
               0.0,1.0,2.0
             */
            while ((st = br.readLine ()) != null) {

                if (cnt % 2 == 0) {
                    coor = st;
                } else {
                    ArrayList<Integer> tiles = new ArrayList<> ();
                    String[] strTiles = st.split (",");
                    for (int i = 0; i < strTiles.length; i++) {
                        tiles.add ((int) Double.parseDouble (strTiles[i]));
                    }
                    table.put (coor, tiles);
                }
                cnt++;
            }
            br.close ();
            // print the hashmap
            //System.out.println(table);
            System.out.println (filename + "Tile Orientation Table read done.");
        } catch (IOException e) {
            e.printStackTrace ();
        }
        return table;
    }

    public static List<ArrayList<Integer>> readDataFromFile (String filePath) {
        List<ArrayList<Integer>> data = new ArrayList<> ();

        try (BufferedReader reader = new BufferedReader (new FileReader (filePath))) {
            String line;
            while ((line = reader.readLine ()) != null) {
                String[] tokens = line.trim ().split (" ");
                ArrayList<Integer> row = new ArrayList<> ();
                for (String token : tokens) {
                    row.add (Integer.parseInt (token));
                }
                data.add (row);
            }
        } catch (IOException e) {
            e.printStackTrace ();
        }

        return data;
    }

    public static int getVideoPaths (String filePath, HashMap<Integer, String> videoIdToPathMap, String outputPath) {
        int lineCount = 0;

        try (BufferedReader br = new BufferedReader (new FileReader (filePath));
             BufferedWriter bw = new BufferedWriter (new FileWriter (outputPath))) {

            String line;
            while ((line = br.readLine ()) != null) {

                String[] parts = line.split (" ");
                if (parts.length > 0) {
                    int videoID = Integer.parseInt (parts[0]);

                    String videoPath = videoIdToPathMap.get (videoID);
                    if (videoPath != null) {

                        String position = extractPosition (videoPath);
                        if (position != null) {
                            bw.write (position);
                            bw.newLine ();
                        }
                    }
                }
                lineCount++;
            }
        } catch (IOException e) {
            e.printStackTrace ();
        }

        return lineCount;
    }

    public static String extractPosition (String videoPath) {
        int startPos = videoPath.indexOf ("(");
        int endPos = videoPath.indexOf (")");
        if (startPos != -1 && endPos != -1 && endPos > startPos) {
            return videoPath.substring (startPos, endPos + 1);
        }
        return null;
    }


    public static void main (String[] args) {

        final int MovePort = 8848;
        final int FuncPort = 8080;
        final int RTSPPort = 8088;
  
        long startTime = System.currentTimeMillis ();
        Utils.predTileTable = readTileTable ("E:\\lyq\\02-myWork\\1.decoding\\codes\\code-theme-decoding_server\\tile_table_1row_4col_120_150.txt");
        Utils.reqTileTable = readTileTable ("E:\\lyq\\02-myWork\\1.decoding\\codes\\code-theme-decoding_server\\tile_table_1row_4col_90_100.txt");
        readIDTable("E:\\lhy\\proj\\process\\allneed\\id2pose_1080p_264.txt",Utils.id2pose,Utils.pose2id);
        Utils.tilesNum = Utils.id2pose.size ();
        int gap = 4000;
        int cachethreadNum = Utils.tilesNum / gap;
        System.out.println ("The total CacheThreads=" + cachethreadNum);
        for (int i = 0; i <= cachethreadNum; i++) {
            new CacheThread("E:\\lhy\\proj\\process\\allneed\\sim_1080p_all_6\\tiles264",i*gap,(i+1)*gap,i).start();
        }
        long prepEndTime = System.currentTimeMillis ();
        System.out.println ("Main thread: preparation done, time used: " + (prepEndTime - startTime) + " ms");

        ServerThread moveServerThread = new ServerThread ("Move Server thread", MovePort, 1);  //port = 8848
        moveServerThread.start ();

        ServerThread funcServerThread = new ServerThread ("ACK Server thread", FuncPort, 2);  //port = 8080
        funcServerThread.start ();

        ServerThread rtspServerThread = new ServerThread ("RTSP Server thread", RTSPPort, 0); //port = 8088
        rtspServerThread.start ();


    }

    public static class ServerThread extends Thread {
        private int PORT;
        private int Type;

        public ServerThread (String name, int port, int type) {
            super (name);
            PORT = port;
            Type = type; // 1, movement server; 2, ACK server
        }

        @Override
        public void run () {
            try (ServerSocket serverSocket = new ServerSocket (PORT)) {

                System.out.println (Thread.currentThread ().getName () + " ready, listening on port " + PORT);
                while (true) {
                    Socket socket = serverSocket.accept ();

                    if (socket == null) {
                        System.out.println (Thread.currentThread ().getName () + " accept socket failed.");
                        break;
                    }
                    System.out.println (Thread.currentThread ().getName () + "Receive connection from: " + socket.getInetAddress ());
                    // at the initialization, receive internal IP address from client
                    BufferedReader reader = new BufferedReader (new InputStreamReader (socket.getInputStream ()));
                    String clientAddr = reader.readLine ();
                    System.out.println (Thread.currentThread ().getName () + "Receive IP from: " + clientAddr);

                    if (Type == 0) {
                        // start the RTSP thread
                        if (!Utils.clientStats.containsKey (clientAddr)) {
                            Utils.clientStats.put (clientAddr, new Stats ());
                            Stats.nextNum++;
                        }
                        System.out.println ("connected client num :" + Stats.nextNum);
                        new RTPThread ("RTP thread " + clientAddr, socket, Stats.nextNum, clientAddr, reader).start ();

                    }
                    if (Type == 1) {
                        // start the prediction thread if the IP belongs to the teacher
                        Utils.teacherAddr = clientAddr;
                        PredictThread predThread = new PredictThread ("Prediction Thread", socket, reader);
                        predThread.start ();
                    } else if (Type == 2) {
                        // wait for the statistic object initialization of the client
                        while (!Utils.clientStats.containsKey (clientAddr)) {
                            try {
                                Thread.sleep (1);
                            } catch (InterruptedException e) {
                                e.printStackTrace ();
                            }
                        }
                        // start the functional thread
                        FuncThread funcThread = new FuncThread ("Functional thread" + clientAddr, socket, clientAddr, reader);
                        funcThread.start ();
                    }
                }
            } catch (IOException ex) {
                System.out.println (Thread.currentThread ().getName () + " exception: " + ex.getMessage ());
                ex.printStackTrace ();
            }
        }
    }
}