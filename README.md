# Expanding dynamic range of an image using Sliding Windows

Sliding window is a method to process frames (adjacent cells) of an array without looping through the array.
By processing frames we understand things like calculation of max, min, avr, median etc across the frame.
The products of processing of each frame are stored in overlay correction arrays.
We use then these precalculated frame-based aggregates to correct value of the initial array, so correction is not global but local.
Used on images, this approach allows selectively add contrast to underexposed areas while not overexposing other areas. 
If we normalize image unselectively, expanding dynamic range to 0...255 will not help resolving details in areas with little local contrast

The Procedure

1. First we set the rolling frame size where aggregation takes place
2. then we expand the image up, down, left and right so frame can go from 1st col/row to last with no hanging out of image boundary
3. then we let the sliding window go and collect aggregates on each step filling the correction arrays (max min avr med)
4. then we estimate global values - max, min, global contrast and boundaries of shadows and highlights (1/3 of contrast, what is not well-grounded assumption yet practical)
5. then we create an array of local contrasts across the frames, this is what is found in each frame
6. then we estimate max, min, avr, med values among the array of local contrasts calculated above
7. then we estimate also standard deviation (sigma) of contrasts and multiply it by 1.5 (assumption), guessing, that if frame contrast is lower than average minus sigma (a.k.a. sigmadown), its a low contrast we cannot tolerate
8. The frame max/min correction - we set new max and min for the frame as median value +/- half of the maximum contrast across ALL frames, clamping these by global max and min in order not to go out of the initial range
9. The frame max/min adjustment - where max value of the frame is in shadows, we expand local max not by half, but by full max contrast across all frames. Local min in highlights we treat likewise.
10. Finally we normalize the image - first with simple min-max filter using max and min across the frame, i.e. contrasting a pixel relative to its neighbours
11. then we normalize the image using sigma-based contrast analysis and checking if the frame is in global highlights and shadows, i.e. we look beyond the context of the particular frame, but carefully not overreaching global min, max and max contrast across frames.
12. we show image histogram, source and two variants of corrected image    
