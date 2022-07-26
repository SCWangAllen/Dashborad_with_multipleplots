結合dash的plotly資料視覺化APP
===
專案目的：磨練自己資料視覺化技巧，並更快速的理解自己處理數據，方便自己快速建立模型
使用程式語言：Python
使用資料集：Kaggle-House Prices - Advanced Regression Techniques
## 一開始的概觀
![image](https://user-images.githubusercontent.com/22531536/180944148-ab861777-6acd-4c74-b80d-a786fda19f07.png)
### 專案發想原因
在做資料分析時，我們很常使用jupyter notebook去觀察資料，但用jupyter notebook的話，會有一些問題。

對我來說，時常要翻來翻去去看資料大概長怎樣，資料型態為何，我處理之後長怎麼樣子，而在同一個檔案裡看，時常看得頭昏腦脹

因此我決定直接將其寫到dash.Datable去看，還能結合css的樣式處理，讓自己能夠更一目了然的看清自己如何處理資料。
***
![image](https://user-images.githubusercontent.com/22531536/180948912-258bee07-8ccd-4b25-adf3-80c21c7944bc.png)
此Datable顯示了此資料集的前五百個資料，能夠給我們一個大致方向資料大概長得如何
***
![image](https://user-images.githubusercontent.com/22531536/180948943-0e49783b-6465-46dd-b329-c62b214ed769.png)
上圖為將pd.DataFrame.info()轉換成我們較容易看的形式，能夠一目了然的看清楚資料型態，資料空值數量等情報
左邊空白處能補上自己理解，或加入新的dash互動元件
***
![image](https://user-images.githubusercontent.com/22531536/180948981-ddc62125-3bb4-43a6-9d4a-70ad4c0c430a.png)
上圖為將pd.DataFrame的describe()轉換成我們較容易看的形式，能夠看出哪些資料(numeric)的數值不合理(結合自己知識判斷)
左邊邊能夠補上自己看資料的理解
***
![image](https://user-images.githubusercontent.com/22531536/180949654-cb862d6a-3c91-460c-be47-cf57f2862e7f.png)
Barchart，我們能在左邊更改x,y軸目標column，並能用color去挑選要分組的columns，能直接去更改圖表的ranhe以及輸出大小。
***
![image](https://user-images.githubusercontent.com/22531536/180949711-62129314-f3d8-4c74-b6b8-bd22e7bde21e.png)
linechart，我們能在左邊更改x,y軸目標column，並能用color去挑選要分組的columns，能直接去更改圖表的range以及輸出大小。
***
![image](https://user-images.githubusercontent.com/22531536/180949737-5b2f6d8a-4dea-4f1b-828f-505b51ff75ee.png)
BoxChart，能夠在左邊更改x、y軸目標，而且x軸支持多個columns同時比較。
***
![image](https://user-images.githubusercontent.com/22531536/180949769-3b53d846-096b-43d1-831e-e6131029b212.png)
Scatter，能夠在左邊更改x、y軸目標，選擇color欄位，能將其變為Bubble plot
***
![image](https://user-images.githubusercontent.com/22531536/180949801-62f0275e-0cc9-4ac4-966d-0ef83ed1b134.png)
DistPlot，能夠觀察目標變數的分配狀況
***
![image](https://user-images.githubusercontent.com/22531536/180949871-88512980-c9e6-46a6-bfda-b29e31020843.png)
能夠直接使用log(方便做模型分析)或是int(縮小倍數，形狀不變，因有些數值太大，會導致memory error)
***
![image](https://user-images.githubusercontent.com/22531536/180950113-9187d352-94aa-46af-aa14-2b205dd301c4.png)
Heatmap，一開始會將所有的變數列出來
***
![image](https://user-images.githubusercontent.com/22531536/180946237-9851aeca-9c3f-40f9-8ae5-1059204a4ea9.png)
我們也能挑選我的想看的個別變數去做個別的heatmap來觀察變數關係。

