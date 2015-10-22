import misc_functions as func
from shutil import copy
import analyze_crossovers as xover
import os

#func.plot_interesting_cases()
#func.plot_article_relative_cases(alpha=0  , phi=6)
#func.plot_article_relative_cases(alpha=0  , phi=0)
#func.plot_article_relative_cases(alpha=6  , phi=0)
#func.plot_article_relative_cases(alpha=6  , phi=6)
#func.plot_article_relative_cases(alpha=12 , phi=0)
#func.plot_article_relative_cases(alpha=12 , phi=6)

xover.plot_bl_crossover_relation(article=True)

image_files = [os.path.join('./article_images',f) \
               for f in os.listdir("./article_images/")\
               if f.endswith('.png')]

for image in image_files:
    copy(image,'../3438747gwkrqg/')
