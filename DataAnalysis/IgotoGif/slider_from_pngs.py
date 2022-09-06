import matplotlib.widgets
import matplotlib.patches
import mpl_toolkits.axes_grid1
import numpy as np 
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider, Button
import cv2

class PageSlider(matplotlib.widgets.Slider):

    def __init__(self, ax, label, numpages = 10, valinit=0, valfmt='%1d', 
                 closedmin=True, closedmax=True,  
                 dragging=True, **kwargs):

        self.facecolor=kwargs.get('facecolor',"w")
        self.activecolor = kwargs.pop('activecolor',"b")
        self.fontsize = kwargs.pop('fontsize', 10)
        self.numpages = numpages

        super(PageSlider, self).__init__(ax, label, 0, numpages, 
                            valinit=valinit, valfmt=valfmt, **kwargs)

        self.poly.set_visible(False)
        self.vline.set_visible(False)
        self.pageRects = []
        for i in range(numpages):
            facecolor = self.activecolor if i==valinit else self.facecolor
            r  = matplotlib.patches.Rectangle((float(i)/numpages, 0), 1./numpages, 1, 
                                transform=ax.transAxes, facecolor=facecolor)
            ax.add_artist(r)
            self.pageRects.append(r)
            ax.text(float(i)/numpages+0.5/numpages, 0.5, str(i+1),  
                    ha="center", va="center", transform=ax.transAxes,
                    fontsize=self.fontsize)
        self.valtext.set_visible(False)

        divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax)
        bax = divider.append_axes("right", size="5%", pad=0.05)
        fax = divider.append_axes("right", size="5%", pad=0.05)
        self.button_back = matplotlib.widgets.Button(bax, label=r'$\u25C0$', color=self.facecolor, hovercolor=self.activecolor)
        self.button_forward = matplotlib.widgets.Button(fax, label=r'$\u25B6$',color=self.facecolor, hovercolor=self.activecolor)
        self.button_back.label.set_fontsize(self.fontsize)
        self.button_forward.label.set_fontsize(self.fontsize)
        self.button_back.on_clicked(self.backward)
        self.button_forward.on_clicked(self.forward)

    def _update(self, event):
        super(PageSlider, self)._update(event)
        i = int(self.val)
        if i >=self.valmax:
            return
        self._colorize(i)

    def _colorize(self, i):
        for j in range(self.numpages):
            self.pageRects[j].set_facecolor(self.facecolor)
        self.pageRects[i].set_facecolor(self.activecolor)

    def forward(self, event):
        current_i = int(self.val)
        i = current_i+1
        if (i < self.valmin) or (i >= self.valmax):
            return
        self.set_val(i)
        self._colorize(i)

    def backward(self, event):
        current_i = int(self.val)
        i = current_i-1
        if (i < self.valmin) or (i >= self.valmax):
            return
        self.set_val(i)
        self._colorize(i)

def draw_pngs(folder="",remove_pngs=False):
    filenames=folder+"/*.png"
    files=glob.glob(filenames)
    frames = []
    for i in files:
        new_frame = mpimg.imread(i)
        frames.append(new_frame)
        # Save into a GIF file that loops forever
        if remove_pngs:
            os.remove(i)
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.18)
    num_pages = len(frames)
    im = ax.imshow(frames[0])

    ax_slider = fig.add_axes([0.1, 0.05, 0.8, 0.04])
    slider = PageSlider(ax_slider, 'Page', num_pages, activecolor="orange")

    def update(val):
        i = int(slider.val)
        im.set_data(frames[i])

    slider.on_changed(update)
    plt.axis("off")
    plt.show() 

def draw_pngs_mp_slide(folder="",remove_pngs=False):
    filenames=folder+"/*.png"
    files=glob.glob(filenames)
    frames = []
    for i in files:
        new_frame = mpimg.imread(i) 
        #reduce size of image to 0.7 
        new_frame = cv2.resize(new_frame, (0,0), fx=0.7, fy=0.7)
        frames.append(new_frame)
        if remove_pngs:
            os.remove(i)
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.15)
    im = ax.imshow(frames[0])
    allowed_values = np.arange( len(frames))
    ax.axis("off")
    ax_slider = plt.axes([0.15, 0.1, 0.65, 0.03])
    slider = Slider(ax_slider, 'Frame', 0, len(frames)-1, valinit=0, valstep=1)
    def update(val):
        frame = slider.val
        im.set_data(frames[int(frame)])
    slider.on_changed(update)
    ax_advance = plt.axes([0.8, 0.025, 0.1, 0.04])
    button = Button(ax_advance, 'Move frames', hovercolor='0.975')
    def advance_2(event):
        if slider.val+2 < len(frames):
            slider.set_val(slider.val+2)
    button.on_clicked(advance_2)
    
    plt.tight_layout()
    plt.show()

folder= "D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\IgotoGif\\pngs" 
draw_pngs_mp_slide(folder)