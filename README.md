## Usage

1. Select the fitting mode. Input *c* for fitting circle, and *r* for fitting rectangle.
2. Input the path of image. For example: *"C:\Users\admin\Desktop\Particles Detection\Samples\img1.jpg"*. Can directly use the "copy path" function in Windows. Quotation marks will be automatically omitted.  
3. Input the physical length of the scale bar. For example, *100*.
4. Draw a line at the scale bar.
5. Select the region of interest. **Scale bar should not be included!**
6. Particles will be marked with red circles and index numbers. Data will be exported in "result.csv". You can delete the mismatch particles manually in csv file.

Example 1 circlr mode:
input
![alt text](https://github.com/acguanine/ParticlesDetection/blob/master/Samples/img1.jpg)

output
![alt text](https://github.com/acguanine/ParticlesDetection/blob/master/Samples/img1/result.jpg)

Example 2 rectangle mode:
input
![alt text](https://github.com/acguanine/ParticlesDetection/blob/master/Samples/img3.jpg)

output
![alt text](https://github.com/acguanine/ParticlesDetection/blob/master/Samples/img3/result.jpg)

## Tips

1. To achieve the best result, the image should have "two-peak" histogram, which means the brightness of particles has a single-peak distribution, and the brightness of background has the other single-peak distribution. The "dazzle light" has significant negative influence to the program. Select the suitable region of interest to avoid that.
2. You can manually optimize the program by modifying  the parameters in *para.json* file. The meaning of parameters can be found in source code.
