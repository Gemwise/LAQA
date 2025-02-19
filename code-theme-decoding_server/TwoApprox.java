import org.apache.commons.math3.util.Pair;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class TwoApprox implements RateAlgo {
    int clientNum;
    String label;
    ArrayList<Integer> u_index;

    public TwoApprox () {
        clientNum = Stats.nextNum;
        label = "LAQA";
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
            d_qualities[cnt] = 1;
            v_qualities[cnt] = 1;
            cnt++;
        }
        // get the requested tiles of current time slot
        String indexPos = Utils.getPosIndex (Utils.predPos[0]);
        float[] ori = Utils.getOri (Utils.predPos[0]);
        String coor = "(" + (int) Utils.calAngle (ori[0]) + "," + (int) Utils.calAngle (ori[1]) + "," + 0 + ")";
        ArrayList<Integer> tiles = Utils.predTileTable.get (coor);

        // density greedy algorithm
        u_index.clear ();
        for (int i = 0; i < clientNum; i++) {
            u_index.add (i);
        }

        final boolean our_method = true;
        final boolean our_method_fairnee = true;

        float d_improve = 0;
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


                if (our_method == false) {
                    //baseline  scheme
                   obj_incre[i] = (Utils.estProb - Utils.ALPHA * delay_portion - Utils.BETA * var_portion);
                } else {
                    //latency scheme
                    obj_incre[i] = (Utils.estProb - Utils.ALPHA * trans_time - Utils.BETA * var_portion - Utils.GAMMA * decode_time);
                }

                density[i] = obj_incre[i] / (rate_high - rate_low);
            }

            int max_index = 0;
            float max_value = 0.0f;
            if (our_method_fairnee == true) {
                // fairness
                List<Integer> u_index_new = getUsersWithQualityWithinLOver2 (d_qualities, u_index, Utils.qualityLevel);

                // Find the user with the highest density among the selected users
                Pair<Integer, Float> maxDensityPair = findMaxDensityIndex (density, u_index_new);
                max_index = maxDensityPair.getKey ();
                max_value = maxDensityPair.getValue ();
            }else {
                 max_index = 0;
                max_value = Float.MIN_VALUE;
                for (int i = 0; i < u_index.size (); i++) {
                    if (density[i] > max_value) {
                        max_value = density[i];
                        max_index = i;
                    }
                }
            }

            if (max_value > 0) {

                int max_user_index = u_index.get (max_index);
                d_qualities[max_user_index] += 1;
                float[] cur_rates = new float[clientNum];
                float total_rate = 0;
                for (int i = 0; i < clientNum; i++) {
                    int quality = d_qualities[i];
                    cur_rates[i] = Utils.calBandwidth (indexPos, tiles, quality);  //unit: MB/s
                    total_rate += cur_rates[i];
                }

                if (cur_rates[max_user_index] >= bandwidth_clients[max_user_index]) {
//                    System.out.println("density greey:" + "User " + max_user_index + " over bandwidth." + bandwidth_clients[max_user_index]);
                }
                if (total_rate >= Utils.RATE_LIMIT_SERVER) {
                    System.out.println("density greey:" + "Total server rate is exceeding the limit !!!!!");
                }

                if (cur_rates[max_user_index] >= bandwidth_clients[max_user_index] ||
                        total_rate >= Utils.RATE_LIMIT_SERVER) {
                    d_qualities[max_user_index] -= 1;
                    u_index.remove (Integer.valueOf (max_user_index));
                } else {
                    d_improve += obj_incre[max_index]; // QoE of every user
                    if (d_qualities[max_user_index] == Utils.qualityLevel)
                        u_index.remove (Integer.valueOf (max_user_index));
                }

            } else {
                u_index.clear ();
                System.out.println("density max_value Negative value encountered: " + max_value);
            }
        }
        
        //value greedy algorithm
        for (int i = 0; i < clientNum; i++) {
            u_index.add (i);
        }

        float v_improve = 0;
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
                if (our_method == false) {
                    //baseline  scheme
                      obj_incre[i] = (Utils.estProb - Utils.ALPHA * delay_portion - Utils.BETA * var_portion);
                }
                else {
                    //latency   scheme
                    obj_incre[i] = (Utils.estProb - Utils.ALPHA * trans_time  - Utils.BETA * var_portion - Utils.GAMMA * decode_time);
                }
            }

            int max_index = 0;
            float max_value = 0.0f;
            if (our_method_fairnee == true) {

                //fairness
                List<Integer> u_index_new = getUsersWithQualityWithinLOver2 (v_qualities, u_index, Utils.qualityLevel);
                // Find the user with the highest density among the selected users
                Pair<Integer, Float> maxIncrePair = findMaxDensityIndex (obj_incre, u_index_new);
                max_index = maxIncrePair.getKey ();
                max_value = maxIncrePair.getValue ();
            }
            else {
                max_index = 0;
                max_value = Float.MIN_VALUE;
                for (int i = 0; i < u_index.size (); i++) {
                    if (obj_incre[i] > max_value) {
                        max_value = obj_incre[i];
                        max_index = i;
                    }
                }
            }

            int max_user_index = u_index.get (max_index);
            if (max_value <= 0) {
                u_index.clear ();
                System.out.println("obj_incre max_value Negative value encountered: " + max_value);
            }
            else {
                v_qualities[max_user_index] += 1;
                float[] cur_rates = new float[clientNum];   //unit: MB/s
                float total_rate = 0;
                for (int i = 0; i < clientNum; i++) {
                    int quality = v_qualities[i];
                    cur_rates[i] = Utils.calBandwidth (indexPos, tiles, quality);
                    total_rate += cur_rates[i];
                }
                
                if (cur_rates[max_user_index] >= bandwidth_clients[max_user_index]) {
//                    System.out.println("value greey:" + "User " + max_user_index + " over bandwidth." + bandwidth_clients[max_user_index]);
                }
                if (total_rate >= Utils.RATE_LIMIT_SERVER) {
                    System.out.println("value greey:" + "Total server rate is exceeding the limit !!!!");
                }
                
                if (cur_rates[max_user_index] >= bandwidth_clients[max_user_index] ||
                        total_rate >= Utils.RATE_LIMIT_SERVER) {
                    v_qualities[max_user_index] -= 1;
                    u_index.remove (Integer.valueOf (max_user_index));
                } else {
                    v_improve += obj_incre[max_index];
                    if (v_qualities[max_user_index] == Utils.qualityLevel)
                        u_index.remove (Integer.valueOf (max_user_index));
                }
            }
        }

        int[] qualities = new int[clientNum];
        if (v_improve > d_improve) {
            // value greedy better
            qualities = v_qualities;
        } else {
            // density greedy better
            qualities = d_qualities;
        }
        // update the qualities in statistics
        for (int i = 0; i < clientNum; i++) {
            Utils.clientStats.get (IPs[i]).curQuality = qualities[i];
        }
    }

    @Override
    public void classifyClient () {

    }

    // Method to get users with quality within L/2 of the minimum quality
    private List<Integer> getUsersWithQualityWithinLOver2(int[] d_qualities, List<Integer> u_index, int qualityLevel) {
        List<ValueWithIndex> valueWithIndices = new ArrayList<>();
        valueWithIndices.clear();

        for (int userIndex : u_index) {
            float qualityValue = d_qualities[userIndex];
            valueWithIndices.add(new ValueWithIndex(qualityValue, userIndex));
        }

        float minValue = Float.MAX_VALUE;
        int minIndex = -1;
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

    // Method to find the index of the maximum density value among a list of indicess subset
    private Pair<Integer, Float> findMaxDensityIndex(float[] density, List<Integer> u_index_subset) {
        int maxUseIndex = 0;
        float maxValue = Float.MIN_VALUE;

        for (int i = 0; i < u_index_subset.size(); i++) {
            int userIndex = u_index_subset.get(i);
            float value = density[userIndex];
            if (value > maxValue) {
                maxValue = value;
                maxUseIndex = userIndex;
            }
        }

        Integer num = u_index_subset.indexOf(maxUseIndex);
        return new Pair<>(num, maxValue); 
    }
}
