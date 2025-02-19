import org.apache.commons.math3.util.Pair;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

import static java.lang.Boolean.*;

public class LAQA_FairnessWithCom implements RateAlgo {
    int clientNum;
    String label;
    ArrayList<Integer> u_index;

    List<Integer> strongClients = new ArrayList<>();
    List<Integer> weakClients = new ArrayList<>();
    List<String> strongClientIPs = new ArrayList<>();
    List<String> weakClientIPs = new ArrayList<>();


    public LAQA_FairnessWithCom () {
        clientNum = Stats.nextNum;
        label = "LAQA_FairnessWithCom";
        u_index = new ArrayList<> ();
    }
    
    @Override
    public void allocate () {
        float[] bandwidth_clients = new float[clientNum];
        int[] d_qualities = new int[clientNum];
        int[] v_qualities = new int[clientNum];
        String[] IPs = new String[clientNum];

        int cnt = 0;
        for (String IP : Utils.clientStats.keySet ()) {
            IPs[cnt] = IP;
            Stats statistics = Utils.clientStats.get (IP);
            bandwidth_clients[cnt] = statistics.estThroughput;
            //start form the lowest quality level
            d_qualities[cnt] = 1;
            v_qualities[cnt] = 1;
            cnt++;
        }
        System.out.println ("bandwidth_clients: " + Arrays.toString (bandwidth_clients));

        // get the requested tiles of current time slot
        String indexPos = Utils.getPosIndex (Utils.predPos[0]);
        float[] ori = Utils.getOri (Utils.predPos[0]);
        String coor = "(" + (int) Utils.calAngle (ori[0]) + "," + (int) Utils.calAngle (ori[1]) + "," + 0 + ")";
        ArrayList<Integer> tiles = Utils.predTileTable.get (coor);

        System.out.println ("current current slot " + (Utils.timeSlot + 1) + " estimated prediction probability: " + String.format("%.2f", Utils.estProb));

        System.out.println("|******** density greedy algorithm ********|");

        List<Integer> strongClientsCopy = new ArrayList<>(strongClients);
        List<Integer> weakClientsCopy = new ArrayList<>(weakClients);

        float d_improve = 0;
        
        u_index.clear ();
        for (int i = 0; i < clientNum; i++) {
            u_index.add (i);
        }
        
        while (!u_index.isEmpty ()) {

            float[] obj_incre = new float[u_index.size ()];
            float[] density = new float[u_index.size ()];

            for (int i = 0; i < u_index.size (); i++) {
                int index = u_index.get (i);
                float rate_low = Utils.calBandwidth (indexPos, tiles, d_qualities[index]);
                float rate_high = Utils.calBandwidth (indexPos, tiles, d_qualities[index] + 1);

                Stats statistics = Utils.clientStats.get (IPs[index]);
                float delay_portion = statistics.predictDelay (rate_high) - statistics.predictDelay (rate_low);
                float trans_time = statistics.predictDelay (rate_high) - statistics.predictDelay (rate_low);

                float decode_time = 0f;
                if (trans_time > 0.0) {

                    float decode_time_high = Utils.decodeTimeMap.get (d_qualities[index] + 1);
                    float decode_time_low = Utils.decodeTimeMap.get (d_qualities[index]);
                    decode_time = decode_time_high - decode_time_low;
                }

                float old_mean = statistics.aveQuality;
                float var_portion = Utils.estProb * (Utils.timeSlot - 1) * (float) (Math.pow (d_qualities[index] + 1 - old_mean, 2) - Math.pow (d_qualities[index] - old_mean, 2)) / Utils.timeSlot;


                if (Utils.our_method == false) {
                    //baseline  scheme
                   obj_incre[i] = (Utils.estProb - Utils.ALPHA * delay_portion - Utils.BETA * var_portion);
                } else {
                    //latency scheme
                    obj_incre[i] = (Utils.estProb - Utils.ALPHA * trans_time - Utils.BETA * var_portion - Utils.GAMMA * decode_time);
                }

                density[i] = obj_incre[i] / (rate_high - rate_low);
            }

            int current_max_index = 0;
            float current_max_value = 0;
            Pair<Integer, Float> densityResult = processClients(u_index,strongClientsCopy,weakClientsCopy,density,d_qualities,Utils.our_method_fairnee);

            current_max_index = densityResult.getKey();
            current_max_value = densityResult.getValue();

            if (current_max_value > 0.0) {
                int user_index = u_index.get(current_max_index);
                System.out.println("density processing: max user: " + user_index + " and value: " + current_max_value);

                d_qualities[user_index] += 1;
                float[] cur_rates = new float[clientNum];
                float total_rate = 0;
                for (int i = 0; i < clientNum; i++) {
                    int quality = d_qualities[i];
                    cur_rates[i] = Utils.calBandwidth (indexPos, tiles, quality);  //unit: MB/s
                    total_rate += cur_rates[i];
                }

                if (cur_rates[user_index] >= bandwidth_clients[user_index]) {
                    System.out.println("density greey:" + "User " + user_index + " over bandwidth." + bandwidth_clients[current_max_index]);
                }
                if (total_rate >= Utils.RATE_LIMIT_SERVER) {
                    System.out.println("density greey:" + "Total server rate is exceeding the limit !!!!!");
                }

                if (cur_rates[user_index] >= bandwidth_clients[user_index] ||
                        total_rate >= Utils.RATE_LIMIT_SERVER) {
                    d_qualities[user_index] -= 1;
                    u_index.remove (Integer.valueOf (user_index));

                    if (strongClientsCopy.contains(user_index)) {
                        strongClientsCopy.remove(Integer.valueOf(user_index));
                        System.out.println("Sconstraint bandwidth,strongClientsCopy.remove.");
                    }

                    else if (weakClientsCopy.contains(user_index)) {
                        weakClientsCopy.remove(Integer.valueOf(user_index));
                        System.out.println("constraint bandwidth,weakClientsCopy.remove.");
                    }
                } else {
                    d_improve += obj_incre[current_max_index];
                    if (d_qualities[user_index] == Utils.qualityLevel) {
                        u_index.remove (Integer.valueOf (user_index));

                        if (strongClientsCopy.contains(user_index)) {
                            strongClientsCopy.remove(Integer.valueOf(user_index));
                            System.out.println("constraint qualityLevel,strongClientsCopy.remove.");
                        }

                        else if (weakClientsCopy.contains(user_index)) {
                            weakClientsCopy.remove(Integer.valueOf(user_index));
                            System.out.println("constraint qualityLevel,weakClientsCopy.remove.");
                        }
                    }
                }
                System.out.println("----------------------------------------------");
                System.out.println("d_qualities: " +Arrays.toString(d_qualities));
            } else {

                u_index.clear ();
                System.out.println("density max_value Negative value encountered: " + current_max_value);
                System.out.println("u_index.clear. No valid clients to process.");
            }
        }
        
        System.out.println("|******** value greedy algorithm ********|");

        strongClientsCopy = new ArrayList<>(strongClients);
        weakClientsCopy = new ArrayList<>(weakClients);
        float v_improve = 0;

        for (int i = 0; i < clientNum; i++) {
            u_index.add (i);
        }

        while (!u_index.isEmpty ()) {

            float[] obj_incre = new float[u_index.size ()];
            
            for (int i = 0; i < u_index.size (); i++) {
                int index = u_index.get (i);
                float rate_low = Utils.calBandwidth (indexPos, tiles, v_qualities[index]);
                float rate_high = Utils.calBandwidth (indexPos, tiles, v_qualities[index] + 1);

                Stats statistics = Utils.clientStats.get (IPs[index]);
                float delay_portion  = statistics.predictDelay (rate_high) - statistics.predictDelay (rate_low);
                float trans_time = statistics.predictDelay (rate_high) - statistics.predictDelay (rate_low);

                float decode_time = 0f;
                if (trans_time > 0.0) {
                    float decode_time_high = Utils.decodeTimeMap.get (v_qualities[index] + 1);
                    float decode_time_low = Utils.decodeTimeMap.get (v_qualities[index]);
                    decode_time = decode_time_high - decode_time_low;
                }

                float old_mean = statistics.aveQuality;
                float var_portion = Utils.estProb * (Utils.timeSlot - 1) * (float) (Math.pow (v_qualities[index] + 1 - old_mean, 2) - Math.pow (v_qualities[index] - old_mean, 2)) / Utils.timeSlot;
                if (Utils.our_method == false) {
                    //baseline  scheme
                      obj_incre[i] = (Utils.estProb - Utils.ALPHA * delay_portion - Utils.BETA * var_portion);
                }
                else {
                    //latency  scheme
                    obj_incre[i] = (Utils.estProb - Utils.ALPHA * trans_time  - Utils.BETA * var_portion - Utils.GAMMA * decode_time);
                }
            }

            Pair<Integer, Float> valueResult = processClients(u_index,strongClientsCopy,weakClientsCopy,obj_incre,v_qualities,Utils.our_method_fairnee);

            int current_max_index = valueResult.getKey();
            float current_max_value = valueResult.getValue();

            if (current_max_value > 0.0) {
                int max_user_index = u_index.get(current_max_index);
                System.out.println("value:processing client max user: " + max_user_index + " and value: " + current_max_value);
                v_qualities[max_user_index] += 1;
                float[] cur_rates = new float[clientNum];   //unit: MB/s
                float total_rate = 0;
                for (int i = 0; i < clientNum; i++) {
                    int quality = v_qualities[i];
                    cur_rates[i] = Utils.calBandwidth (indexPos, tiles, quality);
                    total_rate += cur_rates[i];
                }


                if (cur_rates[max_user_index] >= bandwidth_clients[max_user_index]) {
                    System.out.println("value greey:" + "User " + max_user_index + " over bandwidth:" + bandwidth_clients[max_user_index]);
                }
                if (total_rate >= Utils.RATE_LIMIT_SERVER) {
                    System.out.println("value greey:" + "Total server rate is exceeding the limit");
                }
                
                if (cur_rates[max_user_index] >= bandwidth_clients[max_user_index] || total_rate >= Utils.RATE_LIMIT_SERVER) {
                    v_qualities[max_user_index] -= 1;
                    u_index.remove (Integer.valueOf (max_user_index));

                    if (strongClientsCopy.contains(max_user_index)) {
                        strongClientsCopy.remove(Integer.valueOf(max_user_index));
                        System.out.println("constraint bandwidth,strongClientsCopy.remove." + max_user_index);
                    }

                    else if (weakClientsCopy.contains(max_user_index)) {
                        weakClientsCopy.remove(Integer.valueOf(max_user_index));
                        System.out.println("constraint bandwidth,weakClientsCopy.remove.");
                    }
                } else {
                    v_improve += obj_incre[current_max_index];
                    if (v_qualities[max_user_index] == Utils.qualityLevel){
                        u_index.remove (Integer.valueOf (max_user_index));

                        if (strongClientsCopy.contains(max_user_index)) {
                            strongClientsCopy.remove(Integer.valueOf(max_user_index));
                            System.out.println("constraint qualityLevel,strongClientsCopy.remove.");
                        }

                        else if (weakClientsCopy.contains(max_user_index)) {
                            weakClientsCopy.remove(Integer.valueOf(max_user_index));
                            System.out.println("constraint qualityLevel,weakClientsCopy.remove.");
                        }
                    }
                }
                System.out.println("----------------------------------------------");
                System.out.println("v_qualities: " + Arrays.toString(v_qualities));
                
            }else {
                u_index.clear ();
                System.out.println("obj_incre max_value Negative value encountered: " + current_max_value);
                System.out.println("u_index.clear. No valid clients to process.");
            }
        }

        int[] finalQualities;
        if (v_improve > d_improve) {
            // value greedy better
            finalQualities = v_qualities;
        } else {
            // density greedy better
            finalQualities = d_qualities;
        }
        System.out.println("d_improve: "+ d_improve + " v_improve: " + v_improve);
        System.out.println("d_qualities: " +Arrays.toString(d_qualities));
        System.out.println("v_qualities: " + Arrays.toString(v_qualities));
        System.out.println("finalQualities: " + Arrays.toString(finalQualities));
        // update the qualities in statistics
        for (int i = 0; i < clientNum; i++) {
            Utils.clientStats.get (IPs[i]).curQuality = finalQualities[i];
        }
    }


    @Override
    public void classifyClient(){
        int cnt = 0;
        String[] IPs = new String[clientNum];
        for (String IP : Utils.clientStats.keySet ()) {
            IPs[cnt] = IP;
            cnt++;
        }

        u_index.clear ();
        for (int i = 0; i < clientNum; i++) {
            u_index.add (i);
        }

        System.out.println("u_index contents: " + u_index);
        //u_index contents: [0,1,2]

        for (int i = 0; i < u_index.size(); i++) {
            int index = u_index.get(i);
            String clientIP = IPs[index];
            Boolean isStrongClient = Utils.clientComputationMap.get(clientIP);
            if (isStrongClient != null && isStrongClient) {
                strongClients.add(index);
                strongClientIPs.add(clientIP);
            } else {
                weakClients.add(index);
                weakClientIPs.add(clientIP);
            }
        }
   

        System.out.println("Strong Clients IPs: " + strongClientIPs);
        System.out.println("Weak Clients IPs: " + weakClientIPs);

        System.out.println("Strong Clients Indices: " + strongClients);
        System.out.println("Weak Clients Indices: " + weakClients);

        /*
         Strong Clients IPs: [192.168.50.250]
        Weak Clients IPs: [192.168.50.164, 192.168.50.135]
        Strong Clients Indices: [1]
        Weak Clients Indices: [0, 2]
        * */
    }


    public Pair<Integer, Float> processClients(List<Integer> u_index, List<Integer> strongClients, List<Integer> weakClients, float[] density, int[] d_qualities, boolean our_method_fairnee) {

//        int strong_max_user_index = -1, weak_max_user_index = -1;
        int strong_max_user_index = 0, weak_max_user_index = 0;
        float max_value_strong = Float.NEGATIVE_INFINITY, max_value_weak = Float.NEGATIVE_INFINITY;
        int current_max_index ;
        float current_max_value;


        if (!strongClients.isEmpty()) {

            if (our_method_fairnee) {
                List<Integer> filteredStrongClients = getUsersWithQualityWithinLOver2(d_qualities, strongClients, Utils.qualityLevel);
                if (!filteredStrongClients.isEmpty()) {
                    Pair<Integer, Float> maxDensityPair = findMaxDensityIndex(density,u_index,filteredStrongClients);
                    strong_max_user_index = maxDensityPair.getKey();
                    max_value_strong = maxDensityPair.getValue();
                } else {
                    Pair<Integer, Float> maxDensityPair = findMaxDensityIndex(density,u_index, strongClients);
                    strong_max_user_index = maxDensityPair.getKey();
                    max_value_strong = maxDensityPair.getValue();
                }
            } else {

                Pair<Integer, Float> maxDensityPair = findMaxDensityIndex(density,u_index, strongClients);
                strong_max_user_index = maxDensityPair.getKey();
                max_value_strong = maxDensityPair.getValue();
            }
        } else {

            System.out.println("No strong clients available. Proceeding to weak clients...");
        }


        if (!weakClients.isEmpty()) {

            if (our_method_fairnee) {
                List<Integer> filteredWeakClients = getUsersWithQualityWithinLOver2(d_qualities, weakClients, Utils.qualityLevel);
                if (!filteredWeakClients.isEmpty()) {
                    Pair<Integer, Float> maxDensityPair = findMaxDensityIndex(density,u_index, filteredWeakClients);
                    weak_max_user_index = maxDensityPair.getKey();
                    max_value_weak = maxDensityPair.getValue();
//                    System.out.println("11111111111 % "+  weak_max_user_index +"% " +  max_value_weak);
                } else {
                    Pair<Integer, Float> maxDensityPair = findMaxDensityIndex(density,u_index, weakClients);
                    weak_max_user_index = maxDensityPair.getKey();
                    max_value_weak = maxDensityPair.getValue();
                }
            } else {

                Pair<Integer, Float> maxDensityPair = findMaxDensityIndex(density, u_index,weakClients);
                weak_max_user_index = maxDensityPair.getKey();
                max_value_weak = maxDensityPair.getValue();
            }
        } else {

            System.out.println("No weak clients available.");
        }

        if (max_value_strong >= max_value_weak) {
            current_max_index = strong_max_user_index;
            current_max_value = max_value_strong;
//            System.out.println("strong_max_user_index available-->#" + current_max_index);
        } else {
            current_max_index = weak_max_user_index; 
            current_max_value = max_value_weak;
//            System.out.println("weak_max_user_index available-->*" + current_max_index);
        }

        return new Pair<>(current_max_index, current_max_value);
    }


    // Method to get users with quality within L/2 of the minimum quality
    private List<Integer> getUsersWithQualityWithinLOver2(int[] d_qualities, List<Integer> u_index, int qualityLevel) {
        List<ValueWithIndex> valueWithIndices = new ArrayList<>();
        valueWithIndices.clear();

        for (int index : u_index) {
            float value = d_qualities[index];
            valueWithIndices.add(new ValueWithIndex(value, index));
        }

        float minValue = Float.MAX_VALUE;
        int minIndex = 0;
        for (ValueWithIndex vwi : valueWithIndices) {
            if (vwi.getValue() < minValue) {
                minValue = vwi.getValue();
                minIndex = vwi.getIndex();
            }
        }

        List<ValueWithIndex> valuesWithinLOver2 = new ArrayList<>();
        valuesWithinLOver2.clear();
        for (ValueWithIndex vwi : valueWithIndices) {
            if (Math.abs(vwi.getValue() - minValue) <= qualityLevel / 2)
                valuesWithinLOver2.add(vwi);
        }

        List<Integer> u_index_new = new ArrayList<>();
        u_index_new.clear();

        for (ValueWithIndex vwi : valuesWithinLOver2) {
            int user_index = vwi.getIndex();
            u_index_new.add(user_index);
        }
        return u_index_new;
    }

    // Method to find the index of the maximum density value among a list of indices
    private Pair<Integer, Float> findMaxDensityIndex(float[] density, List<Integer> u_index, List<Integer> indices) {

        int maxUseIndex = 0;
        float maxValue = Float.NEGATIVE_INFINITY;

        for (int userIndex : indices) {
            int newIndex = u_index.indexOf(userIndex);
            float value = density[newIndex];
//            System.out.println("xx22xxdensity ) " + indices.size()+ "% " + value);
            if (value > maxValue) {
                maxValue = value;
                maxUseIndex = newIndex;
            }
        }
//        System.out.println(" ...." + maxUseIndex + " "+  maxValue);
        return new Pair<>(maxUseIndex, maxValue);
    }
}
