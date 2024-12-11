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

        /*对于每一个连接到服务器的客户端 IP，获取其网络统计信息，
        并对其 d_qualities 和 v_qualities 质量进行初始化为1
        */
        int cnt = 0;
        for (String IP : Utils.clientStats.keySet ()) {
            IPs[cnt] = IP;
            Stats statistics = Utils.clientStats.get (IP);
            bandwidth_clients[cnt] = statistics.estThroughput;   //MEA 估计可用带宽

//            bandwidth_clients[cnt] = (float) Double.POSITIVE_INFINITY; // 初始化为正无穷大

/*            int NUM_SAMPLES = Utils.RATE_LIMIT_GUIDELINES.length ; //有几个阈值
            int randomIndex = new Random ().nextInt(NUM_SAMPLES); // 随机选择一个索引
            float rateLimit = Utils.RATE_LIMIT_GUIDELINES[randomIndex]; // 获取对应索引的阈值
            bandwidth_clients[cnt] = rateLimit;*/

            //start form the lowest quality level
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
                    //获取不同quality的解码时间
                    float decode_time_high = Utils.decodeTimeMap.get (d_qualities[index] + 1);
                    float decode_time_low = Utils.decodeTimeMap.get (d_qualities[index]);
                    decode_time = decode_time_high - decode_time_low;
                }

                float old_mean = statistics.aveQuality;
                float var_portion = Utils.estProb * (Utils.timeSlot - 1) * (float) (Math.pow (d_qualities[index] + 1 - old_mean, 2) - Math.pow (d_qualities[index] - old_mean, 2)) / Utils.timeSlot;

                //计算 QoE value increment
                if (our_method == false) {
                    //baseline  scheme
                   obj_incre[i] = (Utils.estProb - Utils.ALPHA * delay_portion - Utils.BETA * var_portion);
                } else {
                    //latency scheme
                    obj_incre[i] = (Utils.estProb - Utils.ALPHA * trans_time - Utils.BETA * var_portion - Utils.GAMMA * decode_time);
                }
                //密度贪婪
                density[i] = obj_incre[i] / (rate_high - rate_low);
            }

            int max_index = 0;
            float max_value = 0.0f;
            if (our_method_fairnee == true) {
                /* 新加功能
                 * fairness: in each quality-level raising iteration, only considering the users in 𝒰′ as candidate users
                 * for increasing the quality level is to avoid too large gap between different users’ quality levels,
                 * achieving the fairness among users.
                 * */
                // New feature for fairness
                List<Integer> u_index_new = getUsersWithQualityWithinLOver2 (d_qualities, u_index, Utils.qualityLevel);

                // Find the user with the highest density among the selected users
                Pair<Integer, Float> maxDensityPair = findMaxDensityIndex (density, u_index_new);
                max_index = maxDensityPair.getKey ();   //是 u_index_new 里的索引
                max_value = maxDensityPair.getValue ();
            }else {
                //or 原作者 ：找到最大的那个 client 的 max_index ，是索引，不是对应的内容。
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
                //获取最大的 client user index
                int max_user_index = u_index.get (max_index);
                d_qualities[max_user_index] += 1; //只把最大的client user 的quality +1
                float[] cur_rates = new float[clientNum];
                float total_rate = 0;
                for (int i = 0; i < clientNum; i++) {
                    int quality = d_qualities[i];
                    cur_rates[i] = Utils.calBandwidth (indexPos, tiles, quality);  //unit: MB/s
                    total_rate += cur_rates[i];
                }
                //当每个条件满足时，会打印出相应的提示信息
                if (cur_rates[max_user_index] >= bandwidth_clients[max_user_index]) {
//                    System.out.println("density greey:" + "User " + max_user_index + " over bandwidth." + bandwidth_clients[max_user_index]);
                }
                if (total_rate >= Utils.RATE_LIMIT_SERVER) {
                    System.out.println("density greey:" + "Total server rate is exceeding the limit !!!!!");
                }

                //受带宽限制
                if (cur_rates[max_user_index] >= bandwidth_clients[max_user_index] ||
                        total_rate >= Utils.RATE_LIMIT_SERVER) {
                    d_qualities[max_user_index] -= 1;
                    u_index.remove (Integer.valueOf (max_user_index));
                } else {
                    d_improve += obj_incre[max_index]; // QoE of every user
                    if (d_qualities[max_user_index] == Utils.qualityLevel)
                        u_index.remove (Integer.valueOf (max_user_index));
                }

            } else { //密度值<0，增益为负，对系统没有共享，停止循还
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

            //计算 QoE for every user
            for (int i = 0; i < u_index.size (); i++) {
                int index = u_index.get (i);
                float rate_low = Utils.calBandwidth (indexPos, tiles, v_qualities[index]);
                float rate_high = Utils.calBandwidth (indexPos, tiles, v_qualities[index] + 1);

                Stats statistics = Utils.clientStats.get (IPs[index]);
                float delay_portion  = statistics.predictDelay (rate_high) - statistics.predictDelay (rate_low);
                float trans_time = statistics.predictDelay (rate_high) - statistics.predictDelay (rate_low);

                float decode_time = 0f;
                if (trans_time > 0.0) {
                    float decode_time_high = Utils.decodeTimeMap.get (v_qualities[index] + 1); //获取不同quality的解码时间
                    float decode_time_low = Utils.decodeTimeMap.get (v_qualities[index]); //获取不同quality的解码时间
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
                /* 新加功能
                 * fairness: in each quality-level raising iteration, only considering the users in 𝒰′ as candidate users
                 * for increasing the quality level is to avoid too large gap between different users’ quality levels,
                 * achieving the fairness among users.
                 * */
                // New feature for fairness
                List<Integer> u_index_new = getUsersWithQualityWithinLOver2 (v_qualities, u_index, Utils.qualityLevel);
                // Find the user with the highest density among the selected users
                Pair<Integer, Float> maxIncrePair = findMaxDensityIndex (obj_incre, u_index_new);
                max_index = maxIncrePair.getKey ();
                max_value = maxIncrePair.getValue ();
            }
            else {
                //or 原作者
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
                //当每个条件满足时，会打印出相应的提示信息
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

        //添加 mapping (qualityValue, userIndex)  //存的是u_index里的内容
        for (int userIndex : u_index) {
            float qualityValue = d_qualities[userIndex];
            valueWithIndices.add(new ValueWithIndex(qualityValue, userIndex));
        }

        //找到 quality level 最小的 user
        float minValue = Float.MAX_VALUE;
        int minIndex = -1;
        for (ValueWithIndex vwi : valueWithIndices) {
            if (vwi.getValue() < minValue) {
                minValue = vwi.getValue();
                minIndex = vwi.getIndex();  //是内容
            }
        }

        //找出 满足quality level 相差在 L/2 的user，把这些组成 new subset,
        List<ValueWithIndex> valuesWithinLOver2 = new ArrayList<>();
        valuesWithinLOver2.clear();
        for (ValueWithIndex vwi : valueWithIndices) {
            if (Math.abs(vwi.getValue() - minValue) <= qualityLevel / 2)
                valuesWithinLOver2.add(vwi);
        }

        List<Integer> u_index_new = new ArrayList<>();
        u_index_new.clear();

        /*for (ValueWithIndex vwi : valuesWithinLOver2) {
            int user_index = u_index.indexOf(vwi.getIndex());  //注意：这里有个index 的转换
            u_index_new.add(user_index);   //存的是u_index的索引
        }*/
        for (ValueWithIndex vwi : valuesWithinLOver2) {
            int user_index = vwi.getIndex(); //存的是u_index的内容，就是有哪些user
            u_index_new.add(user_index);
        }
        return u_index_new;   //若没有符合条件的user,这里会是 NULL list，返回的是内容
    }

    // Method to find the index of the maximum density value among a list of indicess subset
    private Pair<Integer, Float> findMaxDensityIndex(float[] density, List<Integer> u_index_subset) {
        int maxUseIndex = 0;
        float maxValue = Float.MIN_VALUE;

        for (int i = 0; i < u_index_subset.size(); i++) {
            int userIndex = u_index_subset.get(i); // 取出 user index 对应的内容, 如 u_index_subset = [2.4.6]
            float value = density[userIndex];  //取出 user index 对应的density
            if (value > maxValue) {
                maxValue = value;
                maxUseIndex = userIndex;
            }
        }
        //为了和之前的程序统一，这里要返回index，而不是内容。
        Integer num = u_index_subset.indexOf(maxUseIndex);
        return new Pair<>(num, maxValue); //返回：哪一个user,的 value。num 是 u_index_subset里的索引
    }
}
