# drawing example adapted the code from the submitted assignment for STEM course last term

import numpy as np
import cv2
from src.Dorothy import Dorothy
import sounddevice as sd
import torch 

dot = Dorothy()

class MySketch:

    def __init__(self):
        dot.start_loop(self.setup, self.draw)

    def setup(self):
        #Output RAVE from speakers
        latent_dim = 8
        print(sd.query_devices())
        
        rave_id = dot.music.start_rave_stream("models/rav_techno_4059.ts", latent_dim=latent_dim, output_device=3)
        #Explicitly set output device if you are using blackhole to direct audio as
        #a RAVE input (e.g. set this to your speakers to you can hear the output of RAVE)
        # rave_id = dot.music.start_rave_stream("models/taylor.ts", latent_dim=latent_dim, output_device = 1)

        #Random
        # z = torch.randn((1,latent_dim,1))
        # dot.music.update_rave_latent(z) 
        
        #start stream, pass in the number of the device you want to input to RAVE e.g. blackhole
        # device_id = dot.music.start_device_stream(2)
        # dot.music.update_rave_from_stream(device_id)

        # start file stream (to be used as input to RAVE)
        device_id = dot.music.start_file_stream("./audio/disco.wav")
        # set as input to rave (this mutes the source stream, use .gain to hear both)
        dot.music.update_rave_from_stream(device_id)

        d0 = 0.39  # change in latent dimension 0
        d1 = -1.84
        d2 = 1.87
        d3 = 0.87
        d4 = -0.6
        d5 = 1
        d6 = -0.3
        d7 = 1
        z_bias = torch.zeros(1, latent_dim, 1)
        z_bias[:, 0] = torch.linspace(d0, d0, z_bias.shape[-1])
        z_bias[:, 1] = torch.linspace(d1, d1, z_bias.shape[-1])
        z_bias[:, 2] = torch.linspace(d2, d2, z_bias.shape[-1])
        z_bias[:, 3] = torch.linspace(d3, d3, z_bias.shape[-1])
        z_bias[:, 4] = torch.linspace(d4, d4, z_bias.shape[-1])
        z_bias[:, 5] = torch.linspace(d5, d5, z_bias.shape[-1])
        z_bias[:, 6] = torch.linspace(d6, d5, z_bias.shape[-1])
        z_bias[:, 7] = torch.linspace(d7, d7, z_bias.shape[-1])
        #Constant bias
        dot.music.audio_outputs[0].z_bias = z_bias

        # def sine_bias(frame_number, frequency=1, amplitude=1.0, phase=0, sample_rate=44100):
        #     t = frame_number / sample_rate
        #     value = amplitude * math.sin(2 * math.pi * frequency * t + phase)
        #     return value
        
        self.ptr = 0
        # target = [1,2,4,8,16,32,64,128,256]
        # self.t = target[np.random.randint(len(target))]
        def on_new_frame(buffer=np.zeros(2048)):
            n= len(buffer)
            # #Update a new random 
            # # dot.music.audio_outputs[0].z_bias = torch.randn(1,latent_dim,1)*0.1
            # if self.ptr > (self.t*2048):
            #     self.t = target[np.random.randint(len(target))]
            #     z = torch.randn((1,latent_dim,1))
            #     dot.music.update_rave_latent(z) 
            #     print("new z!", self.t)
            #     self.ptr = 0
            # #ORconda
            # #update with oscilating bias
            # val = sine_bias(self.ptr, 0.4, 0.2)
            # dot.music.audio_outputs[0].z_bias = torch.tensor([val for n in range(latent_dim)]).reshape((1,latent_dim,1))

            self.ptr += n
        dot.music.audio_outputs[rave_id].on_new_frame = on_new_frame
        dot.music.play()
        
    def draw(self):
        # the following drawing code mainly inherited from submitted assignment work last term for STEM course
        dot.background((0, 0, 0))
                  
        for bin_num, bin_val in enumerate(dot.music.fft_vals):
            x = bin_num*5
            y = int(bin_val*10)
    
            # randomly set the color changes based on fft
            r = x
            g = x
            b = y 
            music_color = (r, g, b)
            
            # draw dot line using sine wave function, reference code found in: https://stackoverflow.com/questions/10209935/drawing-sine-wave-using-opencv
            # original code found online: y[(int)floor(x)]=10 + 10*sin(2*.1*PI*x)
            y_values = y + y*np.sin(2*np.pi*x*y/100 + 50)
            cv2.line(dot.canvas, (dot.width-x, int(-y_values + 180)), (dot.width-x, int(-y_values + 180)), (255, 255, 255), 1)
            cv2.line(dot.canvas, (x-50, int(y_values/2 + 300)), (x-50, int(y_values/2 + 300)), (255, 255, 255), 1)
                    
            # main effect - circle
            if bin_val < 15:
                cv2.circle(dot.canvas, (dot.width-x, 300), int(y/6), music_color, -1)
                cv2.circle(dot.canvas, (x+250, 270), int(y/10), music_color, -1)
                cv2.circle(dot.canvas, (4*x, 240), int(y/4), music_color, -1)
                cv2.circle(dot.canvas, (dot.width-3*x-250, 210), int(y/5), music_color, -1)
                cv2.circle(dot.canvas, (x, 180), int(y/8), music_color, -1)

            # emphaisis key notes with larger circles
            elif bin_val > 2.5:
                # transparency, reference code found in STEM Week 5 Task Drawing Tips
                # cv2.circle(an.to_alpha(0.7), (2*x, 240), int(y/2), music_color, -1) # using a new canvas for every transparent shape seems causing lags in animation
                cv2.circle(dot.canvas, (x+50, 240), int(y/3), music_color, -1)

        # #Only draw 20 rectangles
        # for i in range(20):
        #     #Get max fft val in window of frequeny bins
        #     window = dot.music.fft_vals[i*win_size:(i+1)*win_size]
        #     val = int(np.mean(window))
        #     width = val*(i*scale)
        #     top_left = (dot.width//2-width,dot.height//2-width)
        #     bottom_right = (dot.width//2+width,dot.height//2+width)
        #     #draw to an alpha layer
        #     new_layer = dot.to_alpha(alpha)
        #     rectangle(new_layer, top_left, bottom_right, (10*val,26*val,143*val), -1)
        # #Call this when you want to render the alpha layers to the canvas (e.g. to draw something else on top of them)
        # dot.update_canvas()
        # # top_left = (dot.width//2-10,dot.height//2-10)
        # # bottom_right = (dot.width//2+10,dot.height//2+10)
        # # rectangle(dot.canvas, top_left, bottom_right, (255,255,255), -1)

MySketch()          







