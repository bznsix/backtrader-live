# bt-ccxt-store-cn
backtrader是一个数据驱动形框架，主要由broker、cerbo、datafeed等几个模块组成\
其中datafeed文件中继承了DataBase基类并重写了def _load方法，这个方法是我们主要的数据来源\
同时在CCXTFeed类当中，也维护了一个状态机，这个状态机有三种状态_ST_LIVE, _ST_HISTORBACK, _ST_OVER\
_ST_LIVE 当前是实盘的数据，每隔订阅的Kline时间向self.line中推送一个最新的bar\
_ST_HISTORBACK 当前是历史数据，由于有些指标需要历史数据所以数据会先加载部分的历史数据\
_ST_OVER 当连接断开后，进入_ST_OVER状态

总的来说，状态机的走向是_ST_HISTORBACK -> ST_LIVE -> _ST_OVER 状态


cerbo类似组装工厂，负责把各个模块组装起来并且按照一定的规则来调用，大致的逻辑是：\

cerbo中有个大循环，会无限的去调用datafeed中的_load函数，这个函数会依据我们传参的interval来确定是否
要向lines中更新数据，当self.lines中的数据得到了更新之后，将会回调我们的strategy函数中的next来执行
我们的既定逻辑进行下单、撤单等操作,这也是为什么我们称之为数据驱动的原因。

