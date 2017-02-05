import matplotlib.pyplot as plt


# Altered from https://gist.github.com/tacaswell/3144287
def zoom_factory(ax,base_scale = 1.5):
    def zoom_fun(event):
        # get the current x and y limits
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        # set the range
        # Get distance from the cursor to the edge of the figure frame
        #cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        #cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        x_left = xdata - cur_xlim[0]
        x_right = cur_xlim[1] - xdata
        y_top = ydata - cur_ylim[0]
        y_bottom = cur_ylim[1] - ydata
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1/base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print(event.button)
        # set new limits
        # ax.set_xlim([xdata - cur_xrange*scale_factor,
        #              xdata + cur_xrange*scale_factor])
        # ax.set_ylim([ydata - cur_yrange*scale_factor,
        #              ydata + cur_yrange*scale_factor])

        ax.set_xlim([xdata - x_left * scale_factor,
                     xdata + x_right * scale_factor])
        ax.set_ylim([ydata - y_top * scale_factor,
                     ydata + y_bottom * scale_factor])

        ax.figure.canvas.draw() # force re-draw

    fig = ax.get_figure() # get the figure of interest
    # attach the call back
    fig.canvas.mpl_connect('scroll_event',zoom_fun)
    #fig.canvas.mpl_connect('button_release_event', rel_fun)