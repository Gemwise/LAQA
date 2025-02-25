# LAQA

Virtual reality (VR) applications have revolutionized digital interaction by providing immersive experiences. 360° VR video streaming has experienced significant growth and popularity as a pivotal VR application. However, the combination of limited network bandwidth and the demand for high-quality videos frequently hinders the achievement of a satisfactory quality of experience (QoE). Although prior methods have enhanced QoE, the effects of decoding latency have been poorly studied. It is technically challenging to design a quality adaptation algorithm that can balance the pursuit of high-quality videos and the limitation of limited bandwidth resources. To address this challenge, we propose an edge-end architecture for 360° VR video streaming and aim to enhance overall QoE by solving a performance optimization problem. Specifically, our experiments on commercial mobile devices in real-world situations reveal that decoding latency significantly influences QoE. First, decoding latency plays a major role in contributing to end-toend latency, which exceeds the transmission latency. Second, decoding latency can differ considerably between devices with varying computational capabilities. Building on this insight, we propose a novel latencyaware quality adaptation (LAQA) algorithm. LAQA lies in developing a solution that can allocate video quality in real-time and enhance overall QoE. LAQA involves not only the quality of the received content, the transmission latency and the quality variance, but also the decoding latency and the fairness of the user quality. Subsequently, we formulate a combinatorial optimization problem to maximize overall QoE. Through extensive validation with experimental data from real-world situations, LAQA offers a promising approach to enhance QoE and ensure fairness performance in different devices. In particular, LAQA achieves 16.77% and 10.66% enhancement over the state-of-the-art combinatorial optimization and reinforcement learning algorithm, respectively, in terms of QoE at 4K resolution. Furthermore, LAQA ensures excellent scalability by simulating the number of users ranging from 15 to 60, making it a robust solution for diverse and growing user scales.



This project consists of two parts, namely simulation experiments and real-world experiment.

- simulation experiment

  We evaluate the performance of LAQA for large-scale users within a trace-based simulation system. We conduct a thorough investigation of our simulation experiments using realistic datasets that encompass user trajectories, network conditions, and bandwidth. Performance is assessed with varying numbers of VR users and at different resolutions (1080P, 2K, 4K). We explore critical metrics such as QoE, quality variance, and latency to highlight the algorithm’s scalability and efficiency in delivering high-quality video experiences.

- real-world experiment

  We evaluate the performance of LAQA with the actual performance of the prototype over commodity WiFi in the wild. Large-scale evaluations through the real user trajectory and different wireless network conditions demonstrate that LAQA achieves higher video quality, lower quality variation, and higher QoE than the state-ofthe-art algorithm. We also demonstrate through experimental analysis that the LAQA algorithm improves QoE more on devices with limited computational capability.

# System Architecture 



The architecture comprises an edge and user layer seamlessly connected via wireless communication. In the edge layer, the access point is connected to the edge server via an Ethernet cable. All videos cached in the edge server are dissected into frames based on a fixed time interval, and these frames are further partitioned into four rectangular tiles (e.g., Tile 0, Tile 1, Tile 2, and Tile 3). These tiles is encoded into multiple quality levels using FFmpeg . Based on the predicted user viewport and the edge server decision-making process, we select the appropriate number of tiles and the corresponding quality levels for transmission. In the user layer, which encompasses 𝑁 users, we utilize two categories of heterogeneous devices, including smartphones and HMDs. The user layer transmits the trajectory of each user’s six degrees of freedom (6 DoF) to the edge layer. 6 DoF are classified into translational and rotational degrees of freedom. The translational degrees of freedom include movement along the X, Y, and Z axes. The rotational degrees of freedom include rotation around these three axes: pitch, yaw, and roll. we have integrated motion prediction into the algorithm design and streamed the relevant part to present these tiles to the user. In reality, any motion prediction model can be incorporated into our architecture to predict the 6 DoF of each user. Therefore, our system considers multiple tiles and does not limit the transmission to just one tile. After receiving all target tiles, users decode them and then assemble them into a panoramic frame and present them on the device.

<div style="text-align: center;">
  <img src="assets/Edge_VR_layered_architecture.png" width="90%" height="90%" />
  <figcaption> Architecture of 360° VR video streaming with edge computing.</figcaption>
</div>

# How the Code Works




# Cite this Work

This is the open source implementation of our TMC 2025 paper "Enhancing Quality of Experience for Collaborative Virtual Reality with Commodity Mobile Devices". If you use the code in an academic work, please cite:

```basic
@ARTICLE{10884912,
  author={Huang, Liang and Li, Yuqi and Liang, Hongyuan and Chi, Kaikai and Wu, Yuan},
  journal={IEEE Transactions on Mobile Computing}, 
  title={Enhanced VR Experience with Edge Computing: The Impact of Decoding Latency}, 
  year={2025},
  pages={1-18},
  doi={10.1109/TMC.2025.3541741}}

```



# decoding_simulation

python


# decoding_server
Java

# decoding_client
Android 
