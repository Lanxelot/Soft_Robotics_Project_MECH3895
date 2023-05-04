import tkinter as tk
import tkinter.messagebox
import customtkinter
import numpy as np
from customtkinter import CTkLabel
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ADCDACPi import ADCDACPi
import RPi.GPIO as GPIO
import time
import subprocess

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
channel = 12
GPIO.setup(channel, GPIO.OUT)
GPIO.output(channel, GPIO.LOW)  # set RPI_PIN LOW to at the start
GPIO.setup(8, GPIO.OUT)
GPIO.output(8, GPIO.LOW)
GPIO.setup(10, GPIO.OUT)
GPIO.output(10, GPIO.LOW)
GPIO.setup(11, GPIO.OUT)
GPIO.output(11, GPIO.LOW)
pwm1 = GPIO.PWM(8, 1)
pwm2 = GPIO.PWM(10, 1)
pwm3 = GPIO.PWM(11, 1)
pwm4 = GPIO.PWM(12, 1)

in1 = 18
in2 = 24
en = 16
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
GPIO.output(22, GPIO.LOW)
p = GPIO.PWM(en, 500)
adcdac = ADCDACPi(2)
adcdac.set_adc_refvoltage(3.3)

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Control Board")
        self.geometry(f"{800}x{480}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.tF = 0
        self.var = customtkinter.IntVar()
        self.var1 = customtkinter.IntVar()
        self.var2 = customtkinter.IntVar()
        self.var3 = customtkinter.IntVar()
        self.Valve1_flag = 0
        self.Valve2_flag = 0
        self.Valve3_flag = 0
        self.Valve4_flag = 0
        self.pat_flag = 0
        self.pattern_flag1 = 0
        self.pattern_flag2 = 0
        self.pattern_flag3 = 0
        self.pattern_flag4 = 0
        self.Stop_data = 0

        # create left sidebar frame with widgets
        self.sidebar_frame_left = customtkinter.CTkTabview(self, width=200, corner_radius=0)
        self.sidebar_frame_left.grid_propagate(False)
        self.sidebar_frame_left.add("Motor Cont")
        self.sidebar_frame_left.add("Pres Cont")
        self.sidebar_frame_left.grid(row=0, column=0, rowspan=4, pady=(0, 10), sticky="nsew")
        self.main_button_1 = customtkinter.CTkButton(master=self.sidebar_frame_left.tab("Motor Cont"),
                                                     fg_color="#36454F", border_width=2,
                                                     text_color=("gray10", "#DCE4EE"), text="Start",
                                                     command=self.start_motor)  # Start pump
        self.main_button_1.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_button_2 = customtkinter.CTkButton(master=self.sidebar_frame_left.tab("Motor Cont"),
                                                     fg_color="#36454F", border_width=2,
                                                     text_color=("gray10", "#DCE4EE"), text="Stop",
                                                     command=self.stop_motor)  # Stop pump
        self.main_button_2.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.slider_2 = customtkinter.CTkSlider(self.sidebar_frame_left.tab("Motor Cont"), orientation="vertical",
                                                from_=0, to=100, number_of_steps=10)
        self.slider_2.grid(row=3, column=0)
        self.textbox = customtkinter.CTkTextbox(self.sidebar_frame_left.tab("Motor Cont"), height=20, width=50)
        self.textbox.place(y=140, x=130)  # .place(y=200, x=130)
        self.Pressure_val = customtkinter.CTkSlider(self.sidebar_frame_left.tab("Pres Cont"), orientation="vertical",
                                                    from_=0, to=13, number_of_steps=13)
        self.Pressure_val.place(y=20, x=100)
        self.Pressure_val.set(0)
        self.Press_textbox = customtkinter.CTkTextbox(self.sidebar_frame_left.tab("Pres Cont"), height=20, width=50)
        self.Press_textbox.place(y=70, x=130)
        self.Data_record_Start = customtkinter.CTkButton(master=self.sidebar_frame_left.tab("Pres Cont"), width=160,
                                                         height=25, border_width=0, corner_radius=8,
                                                         text="STA_Data_Col", command=self.Start_data_Collection)
        self.Data_record_Start.place(y=250, x=25)
        self.Data_record_Stop = customtkinter.CTkButton(master=self.sidebar_frame_left.tab("Pres Cont"), width=160,
                                                        height=25, border_width=0, corner_radius=8, text="STo_Data_Col",
                                                        command=self.Stop_data_Collection)
        self.Data_record_Stop.place(y=300, x=25)
        self.Pressure_val.bind(" <B1-Motion>", self.update_textbox5)
        self.slider_2.bind(" <B1-Motion>", self.update_textbox)
        self.slider_2.set(30)
        self.sidebar_frame_left.grid_rowconfigure(0, weight=0)
        self.sidebar_frame_left.grid_rowconfigure(1, weight=0)
        self.sidebar_frame_left.grid_rowconfigure(2, weight=0)

        # create Right sidebar frame with widgets
        self.man_cont_frame = customtkinter.CTkTabview(self, width=250)
        self.man_cont_frame.grid_propagate(False)
        self.man_cont_frame.grid(row=0, column=2, rowspan=4, pady=(0, 10), sticky="nsew")
        self.man_cont_frame.grid_rowconfigure(0, weight=0)
        self.man_cont_frame.grid_rowconfigure(1, weight=0)
        self.man_cont_frame.grid_rowconfigure(2, weight=0)
        self.man_cont_frame.add("Manual Control")
        self.man_cont_frame.tab("Manual Control").grid_columnconfigure(0, weight=1)
        self.man_cont_frame.add("Automatic control")
        self.man_cont_frame.tab("Automatic control").grid_columnconfigure(0, weight=1)
        self.man_cont_frame.add("Time and Delay")
        self.man_cont_frame.tab("Time and Delay").grid_columnconfigure(0, weight=1)

        self.switch1 = customtkinter.CTkSwitch(master=self.man_cont_frame.tab("Manual Control"), text=f"Valve {1}",
                                               command=self.turn_on_1, variable=self.var)
        self.switch1.grid(row=2, column=0, padx=10, pady=(20, 20))
        self.switch2 = customtkinter.CTkSwitch(master=self.man_cont_frame.tab("Manual Control"), text=f"Valve {2}",
                                               command=self.turn_on_2, variable=self.var1)
        self.switch2.grid(row=3, column=0, padx=10, pady=(0, 20))
        self.switch3 = customtkinter.CTkSwitch(master=self.man_cont_frame.tab("Manual Control"), text=f"Valve {3}",
                                               command=self.turn_on_3, variable=self.var2)
        self.switch3.grid(row=4, column=0, padx=10, pady=(0, 20))
        self.switch4 = customtkinter.CTkSwitch(master=self.man_cont_frame.tab("Manual Control"), text=f"Valve {4}",
                                               command=self.turn_on_4, variable=self.var3)
        self.switch4.grid(row=5, column=0, padx=10, pady=(0, 20))
        self.Main_Pattern1 = customtkinter.CTkButton(master=self.man_cont_frame.tab("Manual Control"), width=110,
                                                     height=25, border_width=0, corner_radius=8, text="Main_Pattern1",
                                                     command=lambda: [self.Pattern_1(), self.TTime_period()])
        self.Main_Pattern1.place(y=240, x=5)
        self.Main_Pattern2 = customtkinter.CTkButton(master=self.man_cont_frame.tab("Manual Control"), width=110,
                                                     height=25, border_width=0, corner_radius=8, text="Main_Pattern2",
                                                     command=lambda: [self.Pattern_2(), self.TTime_period()])
        self.Main_Pattern2.place(y=240, x=125)
        self.Main_Pattern3 = customtkinter.CTkButton(master=self.man_cont_frame.tab("Manual Control"), width=110,
                                                     height=25, border_width=0, corner_radius=8, text="Main_Pattern3",
                                                     command=lambda: [self.Pattern_3(), self.TTime_period()])
        self.Main_Pattern3.place(y=280, x=5)
        self.Main_Pattern4 = customtkinter.CTkButton(master=self.man_cont_frame.tab("Manual Control"), width=110,
                                                     height=25, border_width=0, corner_radius=8, text="Main_Pattern4",
                                                     command=lambda: [self.Pattern_4(), self.TTime_period()])
        self.Main_Pattern4.place(y=280, x=125)
        self.stop_pattern = customtkinter.CTkButton(master=self.man_cont_frame.tab("Manual Control"), width=110,
                                                    height=25, border_width=0, corner_radius=8, text="stop",
                                                    command=self.stop_pattern_func)
        self.stop_pattern.place(y=320, x=55)

        self.Frequency = customtkinter.CTkSlider(self.man_cont_frame.tab("Automatic control"), orientation="vertical",
                                                 from_=0, to=20, number_of_steps=20)
        self.Frequency.place(y=30, x=30)
        self.Duty_Cycle = customtkinter.CTkSlider(self.man_cont_frame.tab("Automatic control"), orientation="vertical",
                                                  from_=0, to=100, number_of_steps=100)
        self.Duty_Cycle.place(y=30, x=150)
        self.textbox1 = customtkinter.CTkTextbox(self.man_cont_frame.tab("Automatic control"), height=20, width=50)
        self.textbox1.place(y=90, x=60)
        self.textbox2 = customtkinter.CTkTextbox(self.man_cont_frame.tab("Automatic control"), height=20, width=50)
        self.textbox2.place(y=90, x=180)
        self.start = customtkinter.CTkButton(master=self.man_cont_frame.tab("Automatic control"), width=110, height=25,
                                             border_width=0, corner_radius=8, text="Start", command=self.check_val)
        self.start.place(y=320, x=5)
        self.stop = customtkinter.CTkButton(master=self.man_cont_frame.tab("Automatic control"), width=110, height=25,
                                            border_width=0, corner_radius=8, text="Stop", command=self.stop_pwm)
        self.stop.place(y=320, x=125)

        self.Valve1 = customtkinter.CTkCheckBox(self.man_cont_frame.tab("Automatic control"), text="Valve 1",
                                                checkbox_width=15, checkbox_height=15, corner_radius=8, width=110,
                                                height=25)
        self.Valve1.place(y=250, x=30)
        self.Valve2 = customtkinter.CTkCheckBox(self.man_cont_frame.tab("Automatic control"), text="Valve 2",
                                                checkbox_width=15, checkbox_height=15, corner_radius=8, width=110,
                                                height=25)
        self.Valve2.place(y=250, x=150)
        self.Valve3 = customtkinter.CTkCheckBox(self.man_cont_frame.tab("Automatic control"), text="Valve 3",
                                                checkbox_width=15, checkbox_height=15, corner_radius=8, width=110,
                                                height=25)
        self.Valve3.place(y=280, x=30)
        self.Valve4 = customtkinter.CTkCheckBox(self.man_cont_frame.tab("Automatic control"), text="Valve 4",
                                                checkbox_width=15, checkbox_height=15, corner_radius=8, width=110,
                                                height=25)
        self.Valve4.place(y=280, x=150)

        self.Time = customtkinter.CTkSlider(self.man_cont_frame.tab("Time and Delay"), orientation="vertical", from_=0,
                                            to=100, number_of_steps=100)
        self.Time.place(y=30, x=30)
        self.Delay = customtkinter.CTkSlider(self.man_cont_frame.tab("Time and Delay"), orientation="vertical", from_=0,
                                             to=100, number_of_steps=100)
        self.Delay.place(y=30, x=150)
        self.Time_box = customtkinter.CTkTextbox(self.man_cont_frame.tab("Time and Delay"), height=20, width=50)
        self.Time_box.place(y=90, x=60)
        self.Delay_box = customtkinter.CTkTextbox(self.man_cont_frame.tab("Time and Delay"), height=20, width=50)
        self.Delay_box.place(y=90, x=180)
        self.appearance_mode_label = customtkinter.CTkLabel(self.man_cont_frame.tab("Time and Delay"), text="Time:",
                                                            anchor="e")
        self.appearance_mode_label.grid(row=0, column=0, padx=10, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.man_cont_frame.tab("Time and Delay"),
                                                                       values=["Light", "Dark", "System"], width=100,
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.place(y=340, x=10)
        self.scaling_label = customtkinter.CTkLabel(self.man_cont_frame.tab("Time and Delay"), text="Delay:",
                                                    anchor="e")
        self.scaling_label.grid(row=0, column=1, padx=10, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.man_cont_frame.tab("Time and Delay"),
                                                               values=["80%", "90%", "100%", "110%", "120%"], width=100,
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.place(y=300, x=120)
        self.Exit_Button = customtkinter.CTkButton(self.man_cont_frame.tab("Time and Delay"), text="Exit", width=100,
                                                   command=self.close_window)
        self.Exit_Button.place(y=255, x=120)
        self.Restart_Button = customtkinter.CTkButton(self.man_cont_frame.tab("Time and Delay"), text="Restart",
                                                      command=self.restart_window, width=100)
        self.Restart_Button.place(y=255, x=10)
        self.Shutdown_Button = customtkinter.CTkButton(self.man_cont_frame.tab("Time and Delay"), text="Shutdown",
                                                       command=self.shutdown_window, width=100)
        self.Shutdown_Button.place(y=300, x=10)
        self.Frequency.bind(" <B1-Motion>", self.update_textbox1)
        self.Duty_Cycle.bind(" <B1-Motion>", self.update_textbox2)
        self.Time.bind(" <B1-Motion>", self.update_textbox3)
        self.Delay.bind(" <B1-Motion>", self.update_textbox4)
        self.Frequency.set(1)
        self.Duty_Cycle.set(0)
        self.Time.set(0)
        self.Delay.set(0)

        # create Graph and oscilloscope
        self.graph = customtkinter.CTkTabview(self, width=250)
        self.graph.add("Oscilloscope")
        self.graph.grid(row=0, column=1, rowspan=3, padx=(10, 10), sticky="ns")
        self.graph.grid_rowconfigure(0, weight=0)
        self.graph.grid_rowconfigure(0, weight=0)

        # Oscilloscope
        self.fig = plt.figure(figsize=(5, 4), dpi=100)

        # Add a subplot to the figure
        self.ax = self.fig.add_subplot(111)

        # Create an empty plot
        self.line, = self.ax.plot([], [])

        # Add labels and titles
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("ADC Value")
        self.ax.set_title("ADC Data Plot")

        # Set the x and y limits of the plot
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 3.3)

        # Create a Tkinter canvas to display the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph.tab("Oscilloscope"))
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # start the animation
        self.update_plot()
        # self.animation()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def update_textbox(self, event):
        self.textbox.delete("1.0", customtkinter.END)
        self.textbox.insert(customtkinter.END, "{0}".format(self.slider_2.get()))
        p.ChangeDutyCycle(int(self.slider_2.get()))

    def update_textbox1(self, event):
        self.textbox1.delete("1.0", customtkinter.END)
        self.textbox1.insert(customtkinter.END, "{0}".format(self.Frequency.get()))
        pwm1.ChangeFrequency(int(self.Frequency.get()))
        pwm2.ChangeFrequency(int(self.Frequency.get()))
        pwm3.ChangeFrequency(int(self.Frequency.get()))
        pwm4.ChangeFrequency(int(self.Frequency.get()))

    def update_textbox2(self, event):
        self.textbox2.delete("1.0", customtkinter.END)
        self.textbox2.insert(customtkinter.END, "{0}".format(self.Duty_Cycle.get()))
        pwm1.ChangeDutyCycle(int(self.Duty_Cycle.get()))
        pwm2.ChangeDutyCycle(int(self.Duty_Cycle.get()))
        pwm3.ChangeDutyCycle(int(self.Duty_Cycle.get()))
        pwm4.ChangeDutyCycle(int(self.Duty_Cycle.get()))

    def update_textbox3(self, event):
        self.Time_box.delete("1.0", customtkinter.END)
        self.Time_box.insert(customtkinter.END, "{0}".format(self.Time.get()))

    def update_textbox4(self, event):
        self.Delay_box.delete("1.0", customtkinter.END)
        self.Delay_box.insert(customtkinter.END, "{0}".format(self.Delay.get()))

    def update_textbox5(self, event):
        self.Press_textbox.delete("1.0", customtkinter.END)
        self.Press_textbox.insert(customtkinter.END, "{0}".format(self.Pressure_val.get()))
        if self.Pressure_val.get() == 0:
            adcdac.set_dac_raw(2, 0)
        if self.Pressure_val.get() == 1:
            adcdac.set_dac_raw(2, 315)
        if self.Pressure_val.get() == 2:
            adcdac.set_dac_raw(2, 630)
        if self.Pressure_val.get() == 3:
            adcdac.set_dac_raw(2, 948)
        if self.Pressure_val.get() == 4:
            adcdac.set_dac_raw(2, 1260)
        if self.Pressure_val.get() == 5:
            adcdac.set_dac_raw(2, 1575)
        if self.Pressure_val.get() == 6:
            adcdac.set_dac_raw(2, 1890)
        if self.Pressure_val.get() == 7:
            adcdac.set_dac_raw(2, 2205)
        if self.Pressure_val.get() == 8:
            adcdac.set_dac_raw(2, 2520)
        if self.Pressure_val.get() == 9:
            adcdac.set_dac_raw(2, 2835)
        if self.Pressure_val.get() == 10:
            adcdac.set_dac_raw(2, 3150)
        if self.Pressure_val.get() == 11:
            adcdac.set_dac_raw(2, 3465)
        if self.Pressure_val.get() == 12:
            adcdac.set_dac_raw(2, 3780)
        if self.Pressure_val.get() == 13:
            adcdac.set_dac_raw(2, 4095)

    def update_plot(self):
        # Read the ADC value
        adc_value = adcdac.read_adc_voltage(1, 0)
        Press = ((adc_value - 0.5) * 10) / 4
        # Append the new data point to the plot data
        x_data = self.line.get_xdata()
        y_data = self.line.get_ydata()
        x_data = np.append(x_data, time.time())
        y_data = np.append(y_data, Press)
        self.line.set_data(x_data, y_data)
        # Update the x and y limits of the plot
        self.ax.set_xlim(max(0, x_data[-1] - 10), x_data[-1] + 1)
        self.ax.set_ylim(0, 10)
        # Redraw the canvas
        self.canvas.draw()
        # Schedule the function to be called again in 100 ms
        self.after(100, self.update_plot)

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def turn_on_1(self):
        if self.var.get() == 1:
            GPIO.output(channel, True)
        if self.var.get() == 0:
            GPIO.output(channel, False)

    def turn_on_2(self):
        if self.var1.get() == 1:
            GPIO.output(8, True)
        if self.var1.get() == 0:
            GPIO.output(8, False)

    def turn_on_3(self):
        if self.var2.get() == 1:
            GPIO.output(10, True)
        if self.var2.get() == 0:
            GPIO.output(10, False)

    def turn_on_4(self):
        if self.var3.get() == 1:
            GPIO.output(11, True)
        if self.var3.get() == 0:
            GPIO.output(11, False)

    def check_val(self):
        self.t = self.Time.get()
        self.d = self.Delay.get()
        self.Valve1_flag = self.Valve1.get()
        self.Valve2_flag = self.Valve2.get()
        self.Valve3_flag = self.Valve3.get()
        self.Valve4_flag = self.Valve4.get()
        self.c(self.t, self.d)

    def c(self, var1, var2):
        if int(var1) > 0 and int(var2) > 0:
            print("Time and Daly")
            self.tF = 1
            self.after(int(var2) * 1000, self.start_pwm)
        if int(var1) == 0 and int(var2) == 0:
            print("Time no Daly")
            self.start_pwm()
        if int(var1) == 0 and int(var2) > 0:
            print(" Daly")
            self.after(int(var2) * 1000, self.start_pwm)
        if int(var1) > 0 and int(var2) == 0:
            print("Time")
            self.tF = 1
            self.start_pwm()

    def start_pwm(self):
        if self.tF == 1:
            self.tF = 0
            if self.Valve1_flag == 1 and self.Valve2_flag == 1 and self.Valve3_flag == 1 and self.Valve4_flag == 1:
                print("All checkboxes are selected1")
                pwm1.start(0)
                pwm2.start(0)
                pwm3.start(0)
                pwm4.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve1_flag == 1 and self.Valve2_flag == 1 and self.Valve3_flag == 1 and self.Valve4_flag == 0:
                print("Checkboxes 1, 2, and 3 are selected")
                pwm1.start(0)
                pwm2.start(0)
                pwm3.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve1_flag == 1 and self.Valve2_flag == 1 and self.Valve4_flag == 1 and self.Valve3_flag == 0:
                print("Checkboxes 1, 2, and 4 are selected")
                pwm1.start(0)
                pwm2.start(0)
                pwm4.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve1_flag == 1 and self.Valve3_flag == 1 and self.Valve4_flag == 1 and self.Valve2_flag == 0:
                print("Checkboxes 1, 3, and 4 are selected")
                pwm1.start(0)
                pwm3.start(0)
                pwm4.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve2_flag == 1 and self.Valve3_flag == 1 and self.Valve4_flag == 1 and self.Valve1_flag == 0:
                print("Checkboxes 2, 3, and 4 are selected")
                pwm2.start(0)
                pwm3.start(0)
                pwm4.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve1_flag == 1 and self.Valve2_flag == 1 and self.Valve3_flag == 0 and self.Valve4_flag == 0:
                print("Checkboxes 1 and 2 are selected")
                pwm1.start(0)
                pwm2.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve1_flag == 1 and self.Valve3_flag == 1 and self.Valve2_flag == 0 and self.Valve4_flag == 0:
                print("Checkboxes 1 and 3 are selected")
                pwm1.start(0)
                pwm3.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve1_flag == 1 and self.Valve4_flag == 1 and self.Valve2_flag == 0 and self.Valve3_flag == 0:
                print("Checkboxes 1 and 4 are selected")
                pwm1.start(0)
                pwm4.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve2_flag == 1 and self.Valve3_flag == 1 and self.Valve1_flag == 0 and self.Valve4_flag == 0:
                print("Checkboxes 2 and 3 are selected")
                pwm2.start(0)
                pwm3.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve2_flag == 1 and self.Valve4_flag == 1 and self.Valve1_flag == 0 and self.Valve3_flag == 0:
                print("Checkboxes 2 and 4 are selected")
                pwm2.start(0)
                pwm4.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve3_flag == 1 and self.Valve4_flag == 1 and self.Valve1_flag == 0 and self.Valve2_flag == 0:
                print("Checkboxes 3 and 4 are selected")
                pwm3.start(0)
                pwm4.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve1_flag == 1 and self.Valve2_flag == 0 and self.Valve3_flag == 0 and self.Valve4_flag == 0:
                print("Checkbox 1 is selected")
                pwm1.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve2_flag == 1 and self.Valve1_flag == 0 and self.Valve3_flag == 0 and self.Valve4_flag == 0:
                print("Checkbox 2 is selected")
                pwm2.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve3_flag == 1 and self.Valve1_flag == 0 and self.Valve2_flag == 0 and self.Valve4_flag == 0:
                print("Checkbox 3 is selected")
                pwm3.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve4_flag == 1 and self.Valve1_flag == 0 and self.Valve2_flag == 0 and self.Valve3_flag == 0:
                print("Checkbox 4 is selected")
                pwm4.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            else:
                print("No checkboxes are selected")

        else:
            if self.Valve1_flag == 1 and self.Valve2_flag == 1 and self.Valve3_flag == 1 and self.Valve4_flag == 1:
                print("All checkboxes are selected1")
                pwm1.start(0)
                pwm2.start(0)
                pwm3.start(0)
                pwm4.start(0)
            elif self.Valve1_flag == 1 and self.Valve2_flag == 1 and self.Valve3_flag == 1 and self.Valve4_flag == 0:
                print("Checkboxes 1, 2, and 3 are selected")
                pwm1.start(0)
                pwm2.start(0)
                pwm3.start(0)
            elif self.Valve1_flag == 1 and self.Valve2_flag == 1 and self.Valve4_flag == 1 and self.Valve3_flag == 0:
                print("Checkboxes 1, 2, and 4 are selected")
                pwm1.start(0)
                pwm2.start(0)
                pwm4.start(0)
            elif self.Valve1_flag == 1 and self.Valve3_flag == 1 and self.Valve4_flag == 1 and self.Valve2_flag == 0:
                print("Checkboxes 1, 3, and 4 are selected")
                pwm1.start(0)
                pwm3.start(0)
                pwm4.start(0)
            elif self.Valve2_flag == 1 and self.Valve3_flag == 1 and self.Valve4_flag == 1 and self.Valve1_flag == 0:
                print("Checkboxes 2, 3, and 4 are selected")
                pwm2.start(0)
                pwm3.start(0)
                pwm4.start(0)
                self.after(int(self.t) * 1000, self.stop_pwm)
            elif self.Valve1_flag == 1 and self.Valve2_flag == 1 and self.Valve3_flag == 0 and self.Valve4_flag == 0:
                print("Checkboxes 1 and 2 are selected")
                pwm1.start(0)
                pwm2.start(0)
            elif self.Valve1_flag == 1 and self.Valve3_flag == 1 and self.Valve2_flag == 0 and self.Valve4_flag == 0:
                print("Checkboxes 1 and 3 are selected")
                pwm1.start(0)
                pwm3.start(0)
            elif self.Valve1_flag == 1 and self.Valve4_flag == 1 and self.Valve2_flag == 0 and self.Valve3_flag == 0:
                print("Checkboxes 1 and 4 are selected")
                pwm1.start(0)
                pwm4.start(0)
            elif self.Valve2_flag == 1 and self.Valve3_flag == 1 and self.Valve1_flag == 0 and self.Valve4_flag == 0:
                print("Checkboxes 2 and 3 are selected")
                pwm2.start(0)
                pwm3.start(0)
            elif self.Valve2_flag == 1 and self.Valve4_flag == 1 and self.Valve1_flag == 0 and self.Valve3_flag == 0:
                print("Checkboxes 2 and 4 are selected")
                pwm2.start(0)
                pwm4.start(0)
            elif self.Valve3_flag == 1 and self.Valve4_flag == 1 and self.Valve1_flag == 0 and self.Valve2_flag == 0:
                print("Checkboxes 3 and 4 are selected")
                pwm3.start(0)
                pwm4.start(0)
            elif self.Valve1_flag == 1 and self.Valve2_flag == 0 and self.Valve3_flag == 0 and self.Valve4_flag == 0:
                print("Checkbox 1 is selected")
                pwm1.start(0)
            elif self.Valve2_flag == 1 and self.Valve1_flag == 0 and self.Valve3_flag == 0 and self.Valve4_flag == 0:
                print("Checkbox 2 is selected")
                pwm2.start(0)
            elif self.Valve3_flag == 1 and self.Valve1_flag == 0 and self.Valve2_flag == 0 and self.Valve4_flag == 0:
                print("Checkbox 3 is selected")
                pwm3.start(0)
            elif self.Valve4_flag == 1 and self.Valve1_flag == 0 and self.Valve2_flag == 0 and self.Valve3_flag == 0:
                print("Checkbox 4 is selected")
                pwm4.start(0)
            else:
                print("No checkboxes are selected")

    def stop_pwm(self):
        print("PWM Stopped")
        pwm1.stop()
        pwm2.stop()
        pwm3.stop()
        pwm4.stop()

    def start_motor(self):
        p.start(1)
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)

    def stop_motor(self):
        p.stop()
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)

    def Pat_123(self):
        if self.pat_flag == 0:
            print("Yes_Pattern1")
            GPIO.output(11, GPIO.LOW)
            GPIO.output(12, GPIO.HIGH)
            self.after(int(self.Duty_Cycle.get()), self.pat1)
        else:
            self.set_flag_pat()

    def pat1(self):
        GPIO.output(8, GPIO.HIGH)
        GPIO.output(12, GPIO.LOW)
        self.after(int(self.Duty_Cycle.get()), self.pat2)

    def pat2(self):
        GPIO.output(10, GPIO.HIGH)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(8, GPIO.LOW)
        self.after(int(self.Duty_Cycle.get()), self.pat3)

    def pat3(self):
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(8, GPIO.LOW)
        GPIO.output(10, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        self.after(int(self.Duty_Cycle.get()), self.Pat_123)

    def Pat12_34(self):
        if self.pat_flag == 0:
            print("Yes_Pattern2")
            GPIO.output(10, GPIO.LOW)
            GPIO.output(11, GPIO.LOW)
            GPIO.output(12, GPIO.HIGH)
            GPIO.output(8, GPIO.HIGH)
            self.after(int(self.Duty_Cycle.get()), self.pat34)
        else:
            self.set_flag_pat()

    def pat34(self):
        GPIO.output(10, GPIO.HIGH)
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(8, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        self.after(int(self.Duty_Cycle.get()), self.Pat12_34)

    def Pat14_23(self):
        if self.pat_flag == 0:
            print("Yes_Pattern3")
            GPIO.output(10, GPIO.LOW)
            GPIO.output(8, GPIO.LOW)
            GPIO.output(12, GPIO.HIGH)
            GPIO.output(11, GPIO.HIGH)
            self.after(int(self.Duty_Cycle.get()), self.pat23)
        else:
            self.set_flag_pat()

    def pat23(self):
        GPIO.output(10, GPIO.HIGH)
        GPIO.output(8, GPIO.HIGH)
        GPIO.output(11, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        self.after(int(self.Duty_Cycle.get()), self.Pat14_23)

    def Pat13_24(self):
        if self.pat_flag == 0:
            print("Yes_Pattern4")
            GPIO.output(11, GPIO.LOW)
            GPIO.output(8, GPIO.LOW)
            GPIO.output(12, GPIO.HIGH)
            GPIO.output(10, GPIO.HIGH)
            self.after(int(self.Duty_Cycle.get()), self.pat24)
        else:
            self.set_flag_pat()

    def pat24(self):
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(8, GPIO.HIGH)
        GPIO.output(10, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        self.after(int(self.Duty_Cycle.get()), self.Pat13_24)

    def stop_pattern_func(self):
        self.pat_flag = 1

    def set_flag_pat(self):
        print("Finished")
        self.pat_flag = 0
        GPIO.output(12, GPIO.LOW)
        GPIO.output(11, GPIO.LOW)
        GPIO.output(10, GPIO.LOW)
        GPIO.output(8, GPIO.LOW)

    def Pattern_1(self):
        self.pattern_flag1 = 1
        self.pattern_delay()

    def Pattern_2(self):
        self.pattern_flag2 = 1
        self.pattern_delay()

    def Pattern_3(self):
        self.pattern_flag3 = 1
        self.pattern_delay()

    def Pattern_4(self):
        self.pattern_flag4 = 1
        self.pattern_delay()

    def pattern_delay(self):
        dd = self.Delay.get()
        if int(dd) > 0:
            print("Daly")
            if self.pattern_flag1 == 1:
                self.pattern_flag1 = 0
                print("Pattern1")
                self.after(int(dd) * 1000, self.Pat_123)
            if self.pattern_flag2 == 1:
                self.pattern_flag2 = 0
                print("Pattern2")
                self.after(int(dd) * 1000, self.Pat12_34)
            if self.pattern_flag3 == 1:
                self.pattern_flag3 = 0
                print("Pattern3")
                self.after(int(dd) * 1000, self.Pat14_23)
            if self.pattern_flag4 == 1:
                self.pattern_flag4 = 0
                print("Pattern4")
                self.after(int(dd) * 1000, self.Pat13_24)

        if int(dd) == 0:
            print("no Daly")
            if self.pattern_flag1 == 1:
                self.pattern_flag1 = 0
                print("Pattern1")
                self.Pat_123()
            if self.pattern_flag2 == 1:
                self.pattern_flag2 = 0
                print("Pattern2")
                self.Pat12_34()
            if self.pattern_flag3 == 1:
                self.pattern_flag3 = 0
                print("Pattern3")
                self.Pat14_23()
            if self.pattern_flag4 == 1:
                self.pattern_flag4 = 0
                print("Pattern4")
                self.Pat13_24()

    def TTime_period(self):
        tt = self.Time.get()
        if int(tt) > 0:
            print("time")
            self.after(int(tt) * 1000, self.stop_pattern_func)
        if int(tt) == 0:
            print("Nothing")

    def Start_data_Collection(self):
        if self.Stop_data == 0:
            self.f = open('/home/ajay/Downloads/Sensor_data', 'a')
            Pressure = adcdac.read_adc_voltage(1, 0)
            textdata = str(Pressure)
            self.f.write(textdata + '\n')
            self.after(1, self.Start_data_Collection)

        else:
            self.Stop_data_Collection()

    def Stop_data_Collection_flag(self):
        self.Stop_data = 1

    def Stop_data_Collection(self):
        self.Stop_data = 0
        self.f.close()

    def close_window(self):
        self.destroy()

    def restart_window(self):
        subprocess.run(['sudo','reboot'])

    def shutdown_window(self):
        subprocess.run(['sudo', 'shutdown','-h','now'])



if __name__ == "__main__":
    app = App()
    app.mainloop()
