
/*定义了接口
* 只有一个函数allocate，其他要是实现这个接口，必须重写这个函数
* 接口只是定义了大家需要统一遵守的规则
* */
public interface RateAlgo {
   void allocate();

	void classifyClient ();
}
