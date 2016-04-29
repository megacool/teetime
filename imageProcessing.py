#1. Convert the RGB color image to grayscale.
#2. Invert the grayscale image to get a negative.
#3. Apply a Gaussian blur to the negative from step 2.
#4. Blend the grayscale image from step 1 with the blurred negative from step 3 using a color dodge.



from PIL import Image, ImageOps, ImageFilter

image = Image.open('image.png')

image = ImageOps.grayscale(image)

image = ImageOps.invert(image)

image = image.filter(ImageFilter.GaussianBlur(radius=2))



image.save('new_image.png') 