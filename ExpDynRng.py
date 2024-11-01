import numpy as np
import cv2
import matplotlib.pyplot as plt
#import bottleneck as bn

perclcontr = np.zeros(20)
pathImage = "test968p.jpg"                                     # select sample image
col_arr = cv2.imread(pathImage)                             # read file into an array
cv2.imshow('test', col_arr)

arr = cv2.cvtColor(col_arr, cv2.COLOR_BGR2GRAY)
sig_ext = 1.5                                               # stdDev extension to activate Loc_contrast override
sw_size = 71                                            # ODD!!!

#arr=np.array([[1,2,3,4,5], [4,5,6,7,8], [8,9,10,11,12], [12,1,0,1,1], [1,0,0,1,0], [0,9,2,1,1]])
#print (arr)

win_row = sw_size                                       # sliding windows Y (rows) ODD VALUE >2
win_col = sw_size                                       # sliding window X (cols) ODD VALUE >2
add_row = win_row - 1                                   # how many rows needed more for sliding window
add_col = win_col - 1                                   # more cols for sliding window
exp_left = np.uint16(add_col / 2)                       # cols added left and right
exp_up = np.uint16(add_row / 2)                         # rows added above and beneath
arr_col1 = arr[:, 0]                                     # first col
arr_col9 = arr[:, -1]                                    # last col
exp_col1 = np.tile(arr_col1, (exp_left, 1)).T             # tile (clone) 1st col and transpose
exp_col9 = np.tile(arr_col9, (exp_left, 1)).T             # tile last col and transpose
arr_exp = np.concatenate((exp_col1, arr), axis=1)       # add array to 1st col
arr_exp = np.concatenate((arr_exp, exp_col9), axis=1)   # add last col to array
arr_row1 = arr_exp[0,:]                                 # first row to add, new cols included
arr_row9 = arr_exp[-1,:]                                # last row, new cols included
exp_row1 = np.tile(arr_row1,(exp_up,1))                 # tile 1st row, no transposing
exp_row9 = np.tile(arr_row9,(exp_up,1))                 # tile last row, no transposing
arr_exp = np.concatenate((exp_row1, arr_exp), axis=0)   # add array with extra cols to cloned 1st row
arr_exp = np.concatenate((arr_exp, exp_row9), axis=0)   # add last row to array

# SLIDING WINDOW AGGREGATION ARRAYS
segs = np.lib.stride_tricks.sliding_window_view(arr_exp,(win_row,win_col))    # fill up array with windows
max_val = np.max(segs, axis=(2,3))                      # array with max values of each window
min_val = np.min(segs, axis=(2,3))                      # array with min values of each window
med_val = np.median(segs, axis=(2,3))                   # array of median values of each window

# CALCULATE CONTRAST MATRIX
gmax = np.max(arr)                                        # global maximum of an image (one digit)
gmin = np.min(arr)                                        # global minimum of an image (one digit)
gcontr = gmax - gmin                                      # global contrast of the image (one digit)
highs = gmax - gcontr/3                                   # global highs lower boundary (2/3 gcontr)
lows = gmin + gcontr/3                                    # global lows upper boundary (1/3 gcontr)
lcontr=np.uint8(((max_val-min_val)/gcontr)*100)           # array of local contrasts relative to global
lc_abs = (max_val - min_val)

# OPERATIONS WITH LOCAL CONTRAST ARRAY (PRODUCES ONE DIGIT PER INDICATOR)
minlcontr = np.min(lcontr)                                # minimal relative contrast of sliding windows
medlcontr = np.median(lcontr)                             # median contrast across the array of relative contrasts
avrlcontr = np.uint8(np.average(lcontr))                  # Average of local contrasts
maxlcontr= np.max(lcontr)                                 # maximal relative contrast of sliding windows
sigma = np.uint8(np.std(lcontr) * sig_ext)                # Standard deviation of local contrasts
sigmadown = np.max(avrlcontr - sigma,0)                      # lower boundary of acceptable contrasts

# MEDIAN VALUE ARRAY FOR MEDIAN BASED WEAK CONTRAST CORRECTION
halfcontr = np.uint8(maxlcontr/2)                         # half-way of the max loc contrast
new_max = np.where((med_val + halfcontr)>gmax, gmax, med_val + halfcontr)   # err <gmax
new_min = np.where((med_val - halfcontr)<gmin, gmin, med_val - halfcontr)

# ADJUSTMENTS OF LOCAL CONTRASTS WHERE THEY FALL BELOW UPPER 90% OF ENTRIES
# thresh_perc = 10                                             # threshold percentile level in contast array
# thresh_perc_val = np.percentile(lcontr, thresh_perc)             # threshold percentile local contrast value
# adj_max = np.where(lcontr > thresh_perc_val, max_val, gmax)
# adj_min = np.where(lcontr > thresh_perc_val, min_val, gmin)

# SINGLE SIGMA BASED ADJUSTMENTS OF LOCAL LOW CONTRASTS -> TO GLOBAL MAX AND MIN
#lcc = np.where(((max_val > highs) AND (min_val > highs)), 1 ,0)
# adj_max = np.where(lcontr > sigmadown, max_val, gmax)       # if local contrast is above, max=lmax else gmax
# adj_min = np.where(lcontr > sigmadown, min_val, gmin)       # if local contrast is above, mix=lmin else gmin

# UPDATED: WEAK CONTRAST WINDOWS WILL HAVE EXPANDED CONTRAST BY MAX_LOC_CONTR DEPENDING ON VALUES BAND (HI, MI, LO)
# test_max = np.min(gmax, med_val + np.uint8(maxlcontr/2))
adj_max = np.where(lcontr > sigmadown, max_val, np.where(max_val < lows, max_val + maxlcontr ,  new_max ))       # -\\-, min=lmin else gmin
adj_min = np.where(lcontr > sigmadown, min_val, np.where(min_val > highs, min_val - maxlcontr , new_min ))     # -\\-, min=lmin else gmin

# UPDATED: WEAK CONTRAST WINDOWS IN HIGHLIGTS AND SHADOWS WILL HAVE EXPANDED CONTRAST BY MAX_LOC_CONTR
# adj_max = np.where(lcontr > sigmadown, max_val, np.where(max_val < lows, max_val + maxlcontr , gmax))       # -\\-, min=lmin else gmin
# adj_min = np.where(lcontr > sigmadown, min_val, np.where(min_val > highs, min_val - maxlcontr , gmin))     # -\\-, min=lmin else gmin

new_arr = np.uint8(255*((arr - min_val)/(max_val - min_val +1)))   #254# -based equalized array
new_arr_bis = np.uint8(255*((arr - adj_min)/(adj_max - adj_min +1)))   #254# -based equalized array
#new_arr_tri = np.uint8(255*((arr - sigmadown)/(sigmaup - sigmadown +1)))   #254# -based equalized array
#arr_cadd = np.hstack((arr_col1, arr))
#arr_mrg=np.vstack([arr_col, arr])

lcontrhist = np.histogram(np.ravel(lcontr))

#max_val2=np.max(segs,0)
#max_val3=np.max(segs,1)
#max_val4=map(np.max(segs),0)
#shape=arr.shape[:-2] + ((arr.shape[-2] - win.shape[-2]) // dc+1,) + ((arr.shape[-1] - win.shape[-1]) // dc+1,) + win.shape
#strides = arr.strides[:-2]+(arr.strides[-2]*dr,) + (arr.strides[-1]*dc,)+arr.strides[-2:]
#print ('shape', shape)
#print ('strides', strides)
#strid=np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)
#newarr = segs - strid

#bna=bn.move_max(arr2,window=3)

#print ('new array', arr_exp)
#print ("additions")
#print (arr_col1)
#print (arr_col9)
#print (arr_row1)
#print (arr_row9)
#print ('sliding wins', segs)
#print ('min', min_val )
#print ('max', max_val )
#print (new_arr)
plt.hist(np.ravel(lcontr), 30)
plt.show()
print ('arr rows:', np.size(arr,0), 'arr cols:', np.size(arr,1))
print ('max rows:', np.size(max_val,0), 'arr cols:', np.size(max_val,1))
print ('min rows:', np.size(min_val,0), 'arr cols:', np.size(min_val,1))
print ('med rows:', np.size(med_val,0), 'arr cols:', np.size(med_val,1))
print (min_val)
print (med_val)
print (max_val)
print ('new condition')
print (np.where((med_val - halfcontr)<gmin, gmin, med_val - halfcontr))
print ('loc conts and global contr',minlcontr, maxlcontr, gmax, gmin, gcontr)
print ('std dev numbers', sigmadown, sigma, avrlcontr, medlcontr)
print ('Histogram', lcontrhist)
cv2.imshow('Result', new_arr)
cv2.imshow('Result2', new_arr_bis)
cv2.waitKey()
