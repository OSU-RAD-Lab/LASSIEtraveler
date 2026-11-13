import matplotlib.pyplot as plt
import numpy as np
import csv
import sys

def localMaximum(x,dev,num,direction):
    index=np.array([], dtype=np.int64)
    n=np.size(x)
    if direction==-1:
        x=np.flip(x)
    # n_range=2*dev+1
    for i in range(dev,n-dev):
        if np.argmax(x[i-dev:i+dev+1])==dev:
            if direction==-1:
                index=np.append(index,n-1-i)
            else:
                index=np.append(index,i)
            if np.size(index)>=num:
                break
    if np.size(index)==0:
        index=np.argmax(x)
        return index
    if num==1:
        return index[0]
    else:
        return index
    
def slope_res(x,y):
    n=np.size(x)
    k=np.zeros(n)
    r=np.zeros(n)
    dot_xy=0.0
    dot_xx=0.0
    dot_yy=0.0
    for i in range(n):
        xi=x[i]
        yi=y[i]
        dot_xy=dot_xy+xi*yi
        dot_xx=dot_xx+xi*xi
        dot_yy=dot_yy+yi*yi
        k[i]=dot_xy/dot_xx
        r[i]=dot_xy*dot_xy/dot_xx/dot_yy
    return k,r

def LR_r2l_kb_res(x,y):
    n=np.size(x)
    k=np.zeros(n)
    b=np.zeros(n)
    r=np.zeros(n)
    sum_x=0.0
    sum_y=0.0
    sum_xy=0.0
    sum_xx=0.0
    sum_yy=0.0
    num=0
    for i in range(n-1,-1,-1):
        num=num+1
        xi=x[i]
        yi=y[i]
        sum_x=sum_x+xi
        sum_y=sum_y+yi
        sum_xy=sum_xy+xi*yi
        sum_xx=sum_xx+xi*xi
        sum_yy=sum_yy+yi*yi
        bar_x=sum_x/num
        bar_y=sum_y/num
        bar_xy=sum_xy/num
        bar_xx=sum_xx/num
        bar_yy=sum_yy/num
        cov_xy=bar_xy-bar_x*bar_y
        var_x=bar_xx-bar_x*bar_x
        var_y=bar_yy-bar_y*bar_y
        k[i]=cov_xy/var_x
        b[i]=bar_y-k[i]*bar_x
        r[i]=cov_xy*cov_xy/var_x/var_y
    return k,b,r

def csv_read_depth_force(filename):
    depth=np.array([], dtype=np.float64)
    force=np.array([], dtype=np.float64)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        lineNum=0
        for row in csv_reader:
            if lineNum>2:
                depth=np.append(depth,float(row[6]))
                force=np.append(force,float(row[2]))
            lineNum+=1
    depth=-depth
    return depth,force

def crust_properties(depth,force,groundHeight,PlotHandle):
    if PlotHandle:
        figure,axis=plt.subplots(2)
        axis[0].plot(depth,force)
    groundHeight+=0.005
    index=np.array([], dtype=np.int64)
    temp=0.0
    for i in range(1,np.size(depth)):
        if depth[i]!=temp:
            index=np.append(index,i)
            temp=depth[i]
    depth=depth[index]
    force=force[index]
    for i in range(np.size(depth)):
        if depth[i]>groundHeight and depth[i+10]>depth[i]:
            i_start=i
            break
    if force[i_start]>0.0:
        for j in range(i_start,-1,-1):
            if force[j]<0.0:
                if -force[i]<force[i+1]:
                    i_start=j
                else:
                    i_start=j+1
                break
    maxdepth=np.max(depth)-depth[i_start]
    for i in range(i_start,np.size(depth)):
        if depth[i]-depth[i_start]>0.98*maxdepth:
            i_end=i
            break
    depth=depth[i_start:i_end]
    depth=depth-depth[0]
    force=force[i_start:i_end]
    n=np.size(depth)

    '''
    n3=0
    threshold=0.05;
    for i in range(n):
        if force[i]>threshold:
            n3=n3+1
            if n3>=3:
                break
        else:
            n3=0
    start_i=i-2
    force=force[start_i:]
    depth=depth[start_i:]
    depth=depth-depth[0]
    '''

    
    for i in range(n):
        if depth[i]-depth[0]>0.01:
            # print(depth[i])
            n_dev=i;
            break
    i_ultimate=localMaximum(force,n_dev,1,1)
    i_basin=np.argmin(force[i_ultimate:])+i_ultimate
    
    i_ultimate=np.argmax(force[i_ultimate:i_basin+1])+i_ultimate
    ultimateDepth=depth[i_ultimate]
    ultimateForce=force[i_ultimate]
    
    basinDepth=depth[i_basin]
    basinForce=force[i_basin]
    
    slope_crust,goodness_crust=slope_res(depth[:i_ultimate+1],force[:i_ultimate+1])
    i_linear_crust=localMaximum(goodness_crust,int(np.floor(0.1*n_dev))+1,1,-1);
    
    yieldDepth=depth[i_linear_crust]
    yieldForce=force[i_linear_crust]
    crustStiffness=slope_crust[i_linear_crust]
    
    slope_sand,intercept_sand,goodness_sand=LR_r2l_kb_res(depth[i_basin:],force[i_basin:])
    i_linear_sand=np.size(depth[i_basin:])-1
    # for i in range(np.size(depth[i_basin:])):
    #     if goodness_sand[i]>0.75:
    #         i_linear_sand=i
    #         break
    if np.size(goodness_sand)>10:
        i_linear_sand=np.argmax(goodness_sand[:-10])
        sandStiffness=slope_sand[i_linear_sand]
        sandInterceptY=intercept_sand[i_linear_sand]
    else:
        sandStiffness=float("nan")
        sandInterceptY=float("nan")
    # if np.size(depth[i_basin:])-i_linear_sand>10:
    #     sandStiffness=slope_sand[i_linear_sand]
    #     sandInterceptY=intercept_sand[i_linear_sand]
    # else:
    #     sandStiffness=float("nan")
    #     sandInterceptY=float("nan")
    depth_sand_linear=depth[i_basin+i_linear_sand]
    sandIntercept=-sandInterceptY/sandStiffness
    if PlotHandle:
        axis[1].plot(depth,force)
        axis[1].plot([0,yieldDepth],[0,crustStiffness*yieldDepth])
        axis[1].plot(ultimateDepth,ultimateForce,marker="o")
        axis[1].plot(basinDepth,basinForce,marker="o")
        if not np.isnan(sandStiffness):
            depth_end=depth[-1]
            axis[1].plot([depth_sand_linear,depth_end],[sandStiffness*depth_sand_linear,sandStiffness*depth_end]+sandInterceptY)
        plt.show()
    return crustStiffness,yieldDepth,yieldForce,ultimateDepth,ultimateForce,basinDepth,basinForce,sandStiffness,sandIntercept, depth_sand_linear, sandInterceptY

# depth,force=csv_read_depth_force('/Users/yifengzhang/Dropbox/Family Room/Yifeng - share/experiment_data/leg/experiment1_Wed_Feb_15_20_59_40_2023.csv')
# depth,force=csv_read_depth_force('/Users/yifengzhang/Dropbox/Family Room/Yifeng - share/experiment_data/leg/experimen2_Wed_Feb_15_21_03_09_2023.csv')
# depth,force=csv_read_depth_force('/Users/yifengzhang/Dropbox/Family Room/Yifeng - share/experiment_data/leg/experimen2_Wed_Feb_15_21_04_30_2023.csv')
# depth,force=csv_read_depth_force('/Users/yifengzhang/Dropbox/Family Room/Yifeng - share/experiment_data/leg/experimen2_Wed_Feb_15_21_05_50_2023.csv')
# depth,force=csv_read_depth_force('/Users/yifengzhang/Dropbox/Family Room/Yifeng - share/experiment_data/leg/experimen2_Wed_Feb_15_21_07_03_2023.csv')
# depth,force=csv_read_depth_force('/Users/yifengzhang/Dropbox/Family Room/Yifeng - share/experiment_data/leg/experiment50_Wed_Feb_15_21_09_25_2023.csv')

if __name__=="__main__":
    # main.py
    PlotHandle=0
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        # print(f"Argument {i:>6}: {arg}")
        if i==1:
            filePath=str(arg)
        elif i==2:
            groundHeight=float(arg)
        elif i==3:
            PlotHandle=int(arg)
    depth,force=csv_read_depth_force(filePath)
    # depth,force=csv_read_depth_force('/home/qianlab/workspace/src/ALLPROJECTS/LASSIE_ROBOT_GUI/experiment_data/leg/_Wed_Mar__1_16_05_02_2023.csv')
    # groundHeight=0.224
    # PlotHandle=1
    crustStiffness,yieldDepth,yieldForce,ultimateDepth,ultimateForce,basinDepth,basinForce,sandStiffness,sandIntercept, depth_sand_linear, sandInterceptY=crust_properties(depth,force,groundHeight,PlotHandle)
    print(f"The crust stiffness is: {crustStiffness}")
    print(f"The ultimate depth is: {ultimateDepth}")
    print(f"The ultimate force is: {ultimateForce}")
    print(f"The basin depth is: {basinDepth}")
    print(f"The basin force is: {basinForce}")
    if not np.isnan(sandStiffness):
        print(f"The sand stiffness is: {sandStiffness}")
        print(f"The intercept is: {sandIntercept}")



