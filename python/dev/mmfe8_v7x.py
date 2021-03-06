#!/usr/bin/env python26

#    by Charlie Armijo, Ken Johns, Bill Hart, Sarah Jones, James Wymer, Kade Gigliotti
#    Experimental Elementary Particle Physics Laboratory
#    Physics Department
#    University of Arizona    
#    armijo at physics.arizona.edu
#    johns at physics.arizona.edu
#
#    This is version 7 of the MMFE8 GUI



import pygtk
pygtk.require('2.0')
import gtk
from array import *
#### On PCROD0 use from Numpy import *
import numpy as np
#from Numeric import *
from struct import *
import gobject 
from subprocess import call
from time import sleep
import sys 
import os
import string
import random
import binstr
import socket
import time
import math
from mmfe8_vmm import vmm
from mmfe8_chan import channel
from mmfe8_userRegs import userRegs
from mmfe8_udp import udp_stuff


############################################################################
############################################################################
###############################               ##############################
###############################  MMFE8 CLASS  ##############################
###############################               ##############################
############################################################################
############################################################################

class MMFE8:
    """
    # ipAddr will be obtained from an xml file in the future
    ipAddr = ["127.0.0.1","192.168.0.130","192.168.0.101","192.168.0.102","192.168.0.103","192.168.0.104","192.168.0.105","192.168.0.106",
              "192.168.0.107","192.168.0.108","192.168.0.109","192.168.0.110","192.168.0.111","192.168.0.112","192.168.0.167"]
    # each is the starting address for the 51 config regs for each vmm 
    mmfeID = 0
    vmmBaseConfigAddr = [0x44A10020,0x44A10038,0x44A10050,0x44A10068,
                         0x44A10080,0x44A10098,0x44A100B0,0x44A100C8,0x44A100E0]
    vmm_cfg_sel_reg = np.zeros((32), dtype=int)
    VMM = []
    UDP_PORT = 50001
    UDP_IP = ""
    chnlReg = np.zeros((51), dtype=int)
    vmmGlobalReset = np.zeros((32), dtype=int)
    start_intTrig_pulseCnt = np.zeros((32), dtype=int)
    byteint = np.zeros((51), dtype=np.uint32)
    byteword = np.zeros((32), dtype=int)
    """


    def destroy(self,widget,data=None):
        # exit gently
        self.stopReadOut = True
        sleep(1) # allow the threads to complete
        print "Goodbye from the MMFE8 GUI!"
        gtk.main_quit()

    def on_erro(self, widget, msg):
        md = gtk.MessageDialog(None,
             gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
             gtk.BUTTONS_OK, msg)
        md.set_title("ERROR")
        md.run()
        md.destroy()
    """
    def udp_client(self, MESSAGE):
        
        sock = socket.socket(socket.AF_INET, # Internet
             socket.SOCK_DGRAM) # UDP 
        sock.settimeout(5)
        try:
            #send data
            print >>sys.stderr, 'sending "%s"' % MESSAGE
            print "to " + self.UDP_IP + ", " + str(self.UDP_PORT)
            sent = sock.sendto(MESSAGE,(self.UDP_IP, self.UDP_PORT))
            #receive response
            print >>sys.stderr, 'waiting for response'
            data, server = sock.recvfrom(4096)
            print >>sys.stderr, 'received:\n' + data
        except:
            print "ERROR:  ", sys.exc_info()[0]
        print "closing socket\n--=====================--\n"
        sock.close()
        return data
        """
   
	
    ######################################################
    #    Configuration Functions
    ######################################################

    def write_vmmConfigRegisters(self,widget):
        """ create full config list """
        current_vmm = int(self.notebook.get_current_page())
        # command strings must be <= 100 chars
        # due to bram limitations on artix7
        self.VMM[current_vmm].entry_SDP_.grab_focus()
        self.VMM[current_vmm].entry_SDT.grab_focus()
        self.button_write.grab_focus()
        #active = self.combo_vmm2_id.get_active()
        #configAddr = self.vmmBaseConfigAddr[0]
        reg = self.VMM[current_vmm].get_channel_val()
        reglist = list(self.VMM[current_vmm].reg.flatten())
        globalreglist = list(self.VMM[current_vmm].globalreg.flatten())
        fullreg = reglist[::-1] + globalreglist[::-1] 
        chars = []
        MESSAGE = ""
        n=0
        m=0
        w=0
        reglist = reglist[::-1]
        for b in range(51):
            self.byteint[b] = 0
            bytelist = fullreg[b*32:(b+1)*32]
            n = n+1
            dummyReg = bytelist[::-1]
            #string = "A" + str(b)
            for bit in range(32):
                self.byteint[b] += int(dummyReg[bit])*pow(2, 31-bit)             
        StartMsg =  "W" +' 0x{0:08X}'.format(self.vmmBaseConfigAddr[0]) #.decode('hex')      
        for c in range(0,51):
            string = "A" + str(c+1)
            myVal = int(self.byteint[c])
            MESSAGE = MESSAGE + ' 0x{0:X}'.format(myVal)
            if (c+1)%6 == 0:
                w = w + 1
                MSGsend = StartMsg + MESSAGE + '\0' + '\n'
                MESSAGE = ""
                m = m + 24
                StartMsg = "W" +' 0x{0:08X}'.format(self.vmmBaseConfigAddr[w])
                self.udp.udp_client(MSGsend,self.UDP_IP,self.UDP_PORT)
                #if self.myDebug:
                #    print "Sent Message to " + self.UDP_IP 
                #    print MSGsend #+ "  {0}".format(m)    
        MSGsend = StartMsg + MESSAGE + '\0' + '\n'
        self.udp.udp_client(MSGsend,self.UDP_IP,self.UDP_PORT)
        #if self.myDebug:
        #    print "Sent Message to " + self.UDP_IP 
        #    print MSGsend
        print "\nWrote to Config Registers\n" 
        self.load_IDs()
        #sleep(5)
        #self.daq_readOut()
        return
               

    def read_reg(self,widget):
        # not currently used -- was intended to read the config stream out
        return        
             
    def print_config(self, widget):
        current_vmm = int(self.notebook.get_current_page())
        ##create and print full config list
        self.VMM[current_vmm].entry_SDP_.grab_focus() # gets data for 
        self.VMM[current_vmm].entry_SDT.grab_focus()
        self.button_print_config.grab_focus()
        reg = self.VMM[current_vmm].get_channel_val()
        reglist = list(self.VMM[current_vmm].reg.flatten())
        globalreglist = list(self.VMM[current_vmm].globalreg.flatten())
        fullreg = reglist[::-1] + globalreglist[::-1]
        #self.buf = [] 
        print "\n\nCONFIG STRING for VMM" + str(current_vmm + 1)
        n=0
        reglist = reglist[::-1]
        #try:
        for b in range(51):
            bytelist = fullreg[b*32:(b+1)*32]
            byteint = 0
            n = n+1
            dummyReg = bytelist[::-1]
            for bit in range(32):
                byteint += int(dummyReg[bit])*pow(2, 31-bit)
            byte = bin(byteint)
            byteword = int(byteint)
            self.chnlReg[b] = byteword
            #print hex(self.chnlReg[b])
            print "0x{0:08x}  reg {1:2d}".format(byteword,n)  
            #except:  IOError as e:
            #    myMsg = "I/O Error"# Reading Ctrl Reg 3:\n{1}".format(e.errno, e.strerror)
            #    #    self.on_erro(widget, myMsg)
        
        return

    ######################################################
    #    Readout Functions
    ######################################################

    def daq_readOut(self):
        fifoCnt = 0
        while fifoCnt == 0:
            msgFifoCnt = "r 0x44A10014 1 \0 \n" # read word count of data fifo
            FifoCntData = self.udp.udp_client(msgFifoCnt,self.UDP_IP,self.UDP_PORT)
            print FifoCntData
            FifoCntStr = string.split(FifoCntData,' ') # split the string to a list
            print FifoCntStr
            fifoCnt = int(FifoCntStr[2],16) # We now have the number of words in the FIFO
        if fifoCnt % 2 == 0:
            fcnt = fifoCnt
        else:
            fcnt = (fifoCnt - 1)
        cycles = fcnt / 10  # reading 10 32-bit data words
        remainder = fcnt % 10
        for i in range(1+cycles)[::-1]:  # reverses the order of the count
            if i == 0:                             # 0 has less than ten words
                m = 2 + remainder
                reads = remainder  # less that 10
            else:
                m = 12 # total words in packet payload
                reads = 10
            msgFifoData = "k 0x44A10010 " + str(reads) + "\n" # read 10 words from fifo
            fifoData = self.udp.udp_client(msgFifoData,self.UDP_IP,self.UDP_PORT)
            n = 2
            while n < m:
                dataList = fifoData.split()
                fifo32 = int(dataList[n],16)
                if fifo32 > 0:
                    fifo32 = fifo32 >> 2  # get rid of first 2 bits (threshold)
                    addr = (fifo32 & 63) + 1 # get channel number as on GUI
                    fifo32 = fifo32 >> 6 # get rid of address
                    amp = fifo32 &  1023 # get amplitude
                    #if (amp & 15) == 0:  # are the lower 4 bit zeros?  if so, tag.
                    #    odd = " ****"
                    #else:
                    #    odd = ""
                    fifo32 = fifo32 >> 10
                    timing = fifo32 & 255
                    fifo32 = fifo32 >> 8  # we will later check for vmm number
                    if (n+1) < 12:
                        fifohigh = int(dataList[n+1],16)
                        print fifohigh
                        BCIDgray = int(fifohigh & 4095) # next change from gray code to int
                        BCid2 = binstr.int_to_b(BCIDgray,16)
                        myBCid = binstr.b_gray_to_bin(BCid2)
                        myIntBCid = binstr.b_to_int(myBCid)
                        fifohigh = fifohigh >> 12  # later we will get the turn number 	 
                    print dataList[n+1] + " "+ dataList[n] + ", addr=" + str(addr) + \
                                   ", amp="+str(amp) + ", time="+str(timing) + ", BCid= " + str(myIntBCid)
                    with open('mmfe8Test.dat', 'a') as myfile:
                                myfile.write(str(int(addr))+'\t'+ str(int(amp))+'\t'+ str(int(timing))+'\t'+ str(myIntBCid) +'\n')
                    n=n+2
                else:
                    print "out of order or no data ="# + str(hex(dataList[n]))
                    n= n+1       

					
					
    def read_xadc(self, widget):
        msg = "w 0x44A10058 1 \0 \n"
        self.udp.udp_client(msg,self.UDP_IP,self.UDP_PORT)
        return

		
    def internal_trigger(self, widget):
        if widget.get_active():
            widget.set_label("ON")
            self.readout_runlength[24] = 1
            #self.udp.udp_client(MSG,self.UDP_IP,self.UDP_PORT)
        else:
            widget.set_label("OFF")
            self.readout_runlength[24] = 0
            #self.udp.udp_client(MSG,self.UDP_IP,self.UDP_PORT)
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.readout_runlength[bit])*pow(2, bit)
        print "readout_runlength = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100F4"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        return

    def set_pulses(self,widget,entry):
        try:
            entry = widget.get_text()
            value = int(entry)
        except ValueError:
            print "Pulses value must be a decimal number"
            print
            return None                
        if (value < 0) or (999 < value): #0x3E7
            print "SDP value out of range"
            print "0 <= Pulses <= 999" 
            return None
        else:
            pulses = value

            ### convert value to list of binary digits ###
            pulses = '{0:010b}'.format(pulses)
            pulses_list = list(pulses)
            pulses_list = map(int, pulses)

            ### add new value to register ###
            for i in range(9,-1,-1):
                self.readout_runlength[9-i] = pulses_list[i] 
            tempInt = 0
            for bit in range(32):
                tempInt += int(self.readout_runlength[bit])*pow(2, bit)
            print "readout_runlength = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
            message = "w 0x44A100F4"
            message = message + ' 0x{0:X}'.format(tempInt)  
            message = message + '\0' + '\n'
            self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
            return
		
    ######################################################
    #    Control Functions
    ######################################################
			
    def start(self, widget):
        tempInt = 0
        self.control[2] = 1
        byteint = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, 31-bit)
            #byteword = int(byteint) 
        message = "w 0x44A100FC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        self.daq_readOut()                   

		sleep(1)
		
        tempInt = 0
        self.control[2] = 0
        byteint = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, 31-bit)
            #byteword = int(byteint) 
        message = "w 0x44A100FC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        #self.daq_readOut()                   
        return
		
    def system_init(self, widget):
        tempInt = 0
        self.control[2] = 1
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, 31-bit)
        message = "w 0x44A100FC" 
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n' 
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)

		sleeep(1)
		
        tempInt = 0
        self.control[2] = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, 31-bit)
        message = "w 0x44A100FC" 
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n' 
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        return

    def reset_global(self, widget):
        tempInt = 0
        self.control[0] = 1
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, 31-bit)
        message = "w 0x44A100FC" 
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n'
        print "VMM Global Reset  " + message  
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT) 
		
		sleeep(1)
		
        tempInt = 0
        self.control[0] = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, 31-bit)
        message = "w 0x44A100FC" 
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n'
        print "VMM Global Reset  " + message  
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT) 
        return
   

    ######################################################
    #    Setup Functions
    ######################################################

    def set_IDs(self, widget):
        self.load_IDs()
        return

    def load_IDs(self):
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.vmm_cfg_sel[bit])*pow(2, bit)
        print "vmm_cfg_sel = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100EC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        
		tempInt = 0
        for bit in range(32):
            tempInt += int(self.readout_runlength[bit])*pow(2, bit)
        print "readout_runlength = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100F4"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        return
       
    def set_board_ip(self, widget, textBox):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            board = active
            self.userRegs.set_udp_ip(self.ipAddr[board])
            self.UDP_IP = self.ipAddr[board]
            print "mmfe8 ip addr = " + self.UDP_IP
            textBox.set_text(str(board))
            self.mmfeID = int(board)
            mmfe_ID = '{0:04b}'.format(self.mmfeID)
            mmfe_ID_list = list(mmfe_ID)
            mmfe_ID_list = map(int, mmfe_ID)
            #print mmfe_ID_list
            ### add new value to register ###
            for i in range(4): #,-1,-1):
                #self.vmm_cfg_sel_reg[28+i] = mmfe_ID_list[i]
                self.vmm_cfg_sel_reg[11-i] = mmfe_ID_list[i]
            print "MMFE8 ID= " + str(self.mmfeID)
    ##==============================================##

    def set_display(self, widget): #, textBox
        active = widget.get_active()
        if active < 0:
            return None
        else:
            my_display = active
            ### convert value to list of binary digits ###
            display = '{0:05b}'.format(int(my_display))
            display_list = list(display)
            #print display_list
            display_list = map(int, display)

            ### add new value to register ###
            for i in range(5):
                self.vmm_cfg_sel[16-i] = display_list[i]

			tempInt = 0
			for bit in range(32):
				tempInt += int(self.vmm_cfg_sel[bit])*pow(2, bit)
			print "vmm_cfg_sel = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
			message = "w 0x44A100EC"
			message = message + ' 0x{0:X}'.format(tempInt)  
			message = message + '\0' + '\n'
			self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
			return
       
    ######################################################
    #    vmm Readout select Functions
    ######################################################
    
    def readoutVmm1_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlengthd[16] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[16] = 0
		load_IDs(self)

    def readoutVmm2_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[17] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[17] = 0
		load_IDs(self)

	def readoutVmm3_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[18] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[18] = 0
		load_IDs(self)

	def readoutVmm4_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[19] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[19] = 0
		load_IDs(self)

	def readoutVmm5_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[20] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[20] = 0
		load_IDs(self)

	def readoutVmm6_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[21] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[21] = 0
		load_IDs(self)

	def readoutVmm7_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[22] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[22] = 0
		load_IDs(self)

	def readoutVmm8_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[23] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[23] = 0
		load_IDs(self)
		
    ######################################################
    #    Reset / config vmm select Functions
    ######################################################

     def Vmm1Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[0] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[0] = 0
		load_IDs(self)
        return

    def Vmm2Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[1] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[1] = 0
		load_IDs(self)
        return

	def Vmm3Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[2] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[2] = 0
		load_IDs(self)
        return
    
	def Vmm4Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[3] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[3] = 0
		load_IDs(self)
        return
    
	def Vmm5Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[4] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[4] = 0
		load_IDs(self)
        return
    
	def Vmm6Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[5] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[5] = 0
		load_IDs(self)
        return
    
	def Vmm7Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[6] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[6] = 0
		load_IDs(self)
        return

	def Vmm8Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[7] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[7] = 0
		load_IDs(self)
        return


    #######################################################################
    #
    #
    #                              __init__    <<==========================
    #
    #
    #######################################################################

    def __init__(self):
        print "loading MMFE8 GUI..."
        print 
        self.tv = gtk.TextView()
        self.tv.set_editable(False)
        self.tv.set_wrap_mode(gtk.WRAP_WORD)
        self.buffer = self.tv.get_buffer()
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        #self.window.set_default_size(1600,1200) ###set_size_request(1440,900)
        self.window.set_default_size(1440,900) ###set_size_request(1440,900)
        self.window.set_resizable(True)
        self.window.set_title("MMFE8 vmm2 Setup GUI (v7.0.0)")
        self.window.set_border_width(0)
        self.notebook = gtk.Notebook()
        self.notebook.set_size_request(-1,0)
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.tab_label_1 = gtk.Label("VMM 1")
        self.tab_label_2 = gtk.Label("VMM 2")
        self.tab_label_3 = gtk.Label("VMM 3")
        self.tab_label_4 = gtk.Label("VMM 4")
        self.tab_label_5 = gtk.Label("VMM 5")
        self.tab_label_6 = gtk.Label("VMM 6")
        self.tab_label_7 = gtk.Label("VMM 7")
        self.tab_label_8 = gtk.Label("VMM 8")
        self.tab_label_9 = gtk.Label("User Defined")
        #self.tab_label_10 = gtk.Label("VMM Output")
        self.VMM = []
        for i in range(8):
            self.VMM.append(vmm())
        self.udp = udp_stuff()
        # ipAddr will be obtained from an xml file in the future
        self.ipAddr = ["127.0.0.1","192.168.0.130","192.168.0.101","192.168.0.102","192.168.0.103","192.168.0.104","192.168.0.105","192.168.0.106",
              "192.168.0.107","192.168.0.108","192.168.0.109","192.168.0.110","192.168.0.111","192.168.0.112","192.168.0.167"]
        # each is the starting address for the 51 config regs for each vmm 
        self.mmfeID = 0
        self.vmmBaseConfigAddr = [0x44A10020,0x44A10038,0x44A10050,0x44A10068,
                         0x44A10080,0x44A10098,0x44A100B0,0x44A100C8,0x44A100E0]

        #self.vmmGlobalReset = np.zeros((32), dtype=int)                #0x44A100EC  #vmm_global_reset          #reset & vmm_gbl_rst_i & vmm_cfg_en_vec( 7 downto 0)
        #self.vmm_cfg_sel_reg = np.zeros((32), dtype=int)                #0x44A100EC  #vmm_cfg_sel               #vmm_2display_i(16 downto 12) & mmfeID(11 downto 8) & vmm_readout_i(7 downto 0)
        self.vmm_cfg_sel = np.zeros((32), dtype=int)                	#0x44A100EC  #vmm_cfg_sel               #vmm_2display_i(16 downto 12) & mmfeID(11 downto 8) & vmm_readout_i(7 downto 0)
        self.cktp_period_dutycycle = np.zeros((32), dtype=int)          #0x44A100F0  #cktp_period_dutycycle     #clk_tp_period_cnt(15 downto 0) & clk_tp_dutycycle_cnt(15 downto 0)
        #self.start_mmfe8 = np.zeros((32), dtype=int)
        self.readout_runlength = np.zeros((32), dtype=int)         		#0x44A100F4  #ReadOut_RunLength    #start & int_trig & pulses(15 downto 0)
        self.xadc = np.zeros((32), dtype=int)                           #0x44A100F8  #xadc                      #read
        self.admux = np.zeros((32), dtype=int)                          #0x44A100F8  #admux                     #write
        self.control = np.zeros((32), dtype=int)                 		#0x44A100FC  #was vmm_global_reset          #reset & vmm_gbl_rst_i & vmm_cfg_en_vec( 7 downto 0)
        self.system_init = np.zeros((32), dtype=int)                     #0x44A10100  #axi_reg_60( 0)            #original reset
        self.userRegs = userRegs()                                      #0x44A10104,08,0C,00,14                 #user_reg_1 #user_reg_2 #user_reg_3 #user_reg_4 #user_reg_5
        self.ds2411_low = np.zeros((32), dtype=int)                     #0x44A10108  #DS411_low                 #Low
        self.ds2411_high = np.zeros((32), dtype=int)                    #0x44A1010C  #DS411_high                #High

        self.UDP_PORT = 50001
        self.UDP_IP = ""
        self.chnlReg = np.zeros((51), dtype=int)
        self.byteint = np.zeros((51), dtype=np.uint32)
        self.byteword = np.zeros((32), dtype=int)

        ####################################################
        ##                    GUI   
        ##                   GLOBAL  
        ##                   BUTTONS 
        ####################################################

        self.button_exit = gtk.Button("EXIT")
        self.button_exit.set_size_request(-1,-1)
        self.button_exit.connect("clicked",self.destroy)

        self.button_start = gtk.Button("Start")
        self.button_start.child.set_justify(gtk.JUSTIFY_CENTER)
        self.label_start = self.button_start.get_children()[0]
        self.button_start.set_size_request(-1,-1)
        self.button_start.connect("clicked",self.start)
        #self.button_start.set_sensitive(False)

        self.label_pulses = gtk.Label("pulses")
        self.label_pulses.set_markup('<span color="blue"><b>Pulses:</b></span>')
        self.label_pulses.set_justify(gtk.JUSTIFY_LEFT)
        self.entry_pulses = gtk.Entry(max=3)
        self.entry_pulses.set_text("0")
        self.entry_pulses.set_editable(True)
        self.entry_pulses.connect("focus-out-event", self.set_pulses)
        self.entry_pulses.connect("activate", self.set_pulses, self.entry_pulses)

        #self.combo_pulses.connect("changed",self.set_pulses)
        #self.combo_pulses.set_active(0)
        self.box_pulses = gtk.HBox()
        self.box_pulses.pack_start(self.label_pulses, expand=True)
        self.box_pulses.pack_start(self.entry_pulses, expand=False)

        self.label_pulses2 = gtk.Label("999 == Continuous")
        self.label_pulses2.set_markup('<span color="purple"><b>999 == Continuous</b></span>')
        self.label_pulses2.set_justify(gtk.JUSTIFY_CENTER)

        self.button_resetVMM = gtk.Button("VMM Global Reset")
        self.button_resetVMM.set_size_request(-1,-1)
        self.button_resetVMM.connect("clicked",self.reset_global)

        self.button_SystemInit = gtk.Button("System Reset + VMM Load")
        self.button_SystemInit.set_size_request(-1,-1)
        self.button_SystemInit.connect("clicked",self.system_init) ###<<<======
        #self.button_resetVMM.set_sensitive(False)

        self.label_vmmGlobal_Reset = gtk.Label("vmm2")
        self.label_vmmGlobal_Reset.set_markup('<span color="blue"><b>VMMs to Reset / Load</b></span>')
        self.label_vmmGlobal_Reset.set_justify(gtk.JUSTIFY_CENTER)

        self.check_button_vmm1_reset = gtk.CheckButton()
        self.check_button_vmm1_reset.connect("toggled", self.Vmm1Reset_callback)
        self.check_button_vmm2_reset = gtk.CheckButton()
        self.check_button_vmm2_reset.connect("toggled", self.Vmm2Reset_callback)
        self.check_button_vmm3_reset = gtk.CheckButton()
        self.check_button_vmm3_reset.connect("toggled", self.Vmm3Reset_callback)
        self.check_button_vmm4_reset = gtk.CheckButton()
        self.check_button_vmm4_reset.connect("toggled", self.Vmm4Reset_callback)
        self.check_button_vmm5_reset = gtk.CheckButton()
        self.check_button_vmm5_reset.connect("toggled", self.Vmm5Reset_callback)
        self.check_button_vmm6_reset = gtk.CheckButton()
        self.check_button_vmm6_reset.connect("toggled", self.Vmm6Reset_callback)
        self.check_button_vmm7_reset = gtk.CheckButton()
        self.check_button_vmm7_reset.connect("toggled", self.Vmm7Reset_callback)
        self.check_button_vmm8_reset = gtk.CheckButton()        
        self.check_button_vmm8_reset.connect("toggled", self.Vmm8Reset_callback)
        self.label_vmmReset_1 = gtk.Label("1")
        self.label_vmmReset_2 = gtk.Label("2")
        self.label_vmmReset_3 = gtk.Label("3")
        self.label_vmmReset_4 = gtk.Label("4")
        self.label_vmmReset_5 = gtk.Label("5")
        self.label_vmmReset_6 = gtk.Label("6")
        self.label_vmmReset_7 = gtk.Label("7")
        self.label_vmmReset_8 = gtk.Label("8")

        self.vmmReset_table1 = gtk.Table(rows=2, columns=8, homogeneous=True)
        self.vmmReset_table1.attach(self.label_vmmReset_1, left_attach=0, right_attach=1, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm1_reset, left_attach=0, right_attach=1, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_2, left_attach=1, right_attach=2, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm2_reset, left_attach=1, right_attach=2, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_3, left_attach=2, right_attach=3, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm3_reset, left_attach=2, right_attach=3, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_4, left_attach=3, right_attach=4, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm4_reset, left_attach=3, right_attach=4, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_5, left_attach=4, right_attach=5, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm5_reset, left_attach=4, right_attach=5, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_6, left_attach=5, right_attach=6, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm6_reset, left_attach=5, right_attach=6, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_7, left_attach=6, right_attach=7, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm7_reset, left_attach=6, right_attach=7, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_8, left_attach=7, right_attach=8, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm8_reset, left_attach=7, right_attach=8, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)


        self.label_But_Space1 = gtk.Label(" ")
        self.label_But_Space2 = gtk.Label(" ")        
        self.label_But_Space3 = gtk.Label(" ")
        self.label_But_Space4 = gtk.Label(" ")
        self.label_But_Space5 = gtk.Label(" ") 
        self.label_But_Space8 = gtk.Label(" ")
        self.label_But_Space9 = gtk.Label(" ")
        self.label_But_Space10 = gtk.Label(" ")      


        self.label_vmmReadoutMask = gtk.Label("vmm2")
        self.label_vmmReadoutMask.set_markup('<span color="blue"><b>VMM Readout Enable</b></span>')
        self.label_vmmReadoutMask.set_justify(gtk.JUSTIFY_CENTER)

        self.check_button_vmm1_readout = gtk.CheckButton()
        self.check_button_vmm1_readout.connect("toggled", self.readoutVmm1_callback)
        self.check_button_vmm2_readout = gtk.CheckButton()
        self.check_button_vmm2_readout.connect("toggled", self.readoutVmm2_callback)
        self.check_button_vmm3_readout = gtk.CheckButton()
        self.check_button_vmm3_readout.connect("toggled", self.readoutVmm3_callback)
        self.check_button_vmm4_readout = gtk.CheckButton()
        self.check_button_vmm4_readout.connect("toggled", self.readoutVmm4_callback)
        self.check_button_vmm5_readout = gtk.CheckButton()
        self.check_button_vmm5_readout.connect("toggled", self.readoutVmm5_callback)
        self.check_button_vmm6_readout = gtk.CheckButton()
        self.check_button_vmm6_readout.connect("toggled", self.readoutVmm6_callback)
        self.check_button_vmm7_readout = gtk.CheckButton()
        self.check_button_vmm7_readout.connect("toggled", self.readoutVmm7_callback)
        self.check_button_vmm8_readout = gtk.CheckButton()
        self.check_button_vmm8_readout.connect("toggled", self.readoutVmm8_callback)        
        self.label_vmmReadout_1 = gtk.Label("1")
        self.label_vmmReadout_2 = gtk.Label("2")
        self.label_vmmReadout_3 = gtk.Label("3")
        self.label_vmmReadout_4 = gtk.Label("4")
        self.label_vmmReadout_5 = gtk.Label("5")
        self.label_vmmReadout_6 = gtk.Label("6")
        self.label_vmmReadout_7 = gtk.Label("7")
        self.label_vmmReadout_8 = gtk.Label("8")

        self.vmmReadout_table1 = gtk.Table(rows=2, columns=8, homogeneous=True)
        self.vmmReadout_table1.attach(self.label_vmmReadout_1, left_attach=0, right_attach=1, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm1_readout, left_attach=0, right_attach=1, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_2, left_attach=1, right_attach=2, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm2_readout, left_attach=1, right_attach=2, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_3, left_attach=2, right_attach=3, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm3_readout, left_attach=2, right_attach=3, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_4, left_attach=3, right_attach=4, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm4_readout, left_attach=3, right_attach=4, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_5, left_attach=4, right_attach=5, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm5_readout, left_attach=4, right_attach=5, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_6, left_attach=5, right_attach=6, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm6_readout, left_attach=5, right_attach=6, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_7, left_attach=6, right_attach=7, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm7_readout, left_attach=6, right_attach=7, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_8, left_attach=7, right_attach=8, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm8_readout, left_attach=7, right_attach=8, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)



        self.button_write = gtk.Button("Write to Config Buffer")
        self.button_write.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_write.set_size_request(-1,-1)        
        self.button_write.connect("clicked",self.write_vmmConfigRegisters)
        self.button_read_reg = gtk.Button("READ Config\nRegisters")
        self.button_read_reg.set_sensitive(False)
        self.button_read_reg.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_read_reg.set_size_request(-1,-1)
        self.button_read_reg.connect("clicked",self.read_reg)
        self.label_internal_trigger =  gtk.Label("Internal Trigger:    ")
        self.label_internal_trigger.set_markup('<span color="blue"><b>Internal Trigger:    </b></span>')
        self.button_internal_trigger = gtk.ToggleButton("OFF")
        self.button_internal_trigger.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_internal_trigger.connect("clicked",self.internal_trigger)
        self.button_internal_trigger.set_size_request(-1,-1)
        self.button_read_XADC = gtk.Button("Read XADC")
        self.button_read_XADC.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_read_XADC.connect("clicked",self.read_xadc)
        self.button_read_XADC.set_size_request(-1,-1)
        self.button_print_config = gtk.Button("Print Config Load")
        self.button_print_config.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_print_config.set_size_request(-1,-1)
        self.button_print_config.connect("clicked",self.print_config)

        # Choose Board

        self.label_mmfe8_id = gtk.Label("mmfe8")
        self.label_mmfe8_id.set_markup('<span color="blue"><b>mmfe\nID</b></span>')
        self.label_mmfe8_id.set_justify(gtk.JUSTIFY_CENTER)
        self.entry_mmfeID = gtk.Entry(max=3)
        self.entry_mmfeID.set_text(str(self.mmfeID))
        self.entry_mmfeID.set_editable(False)
        
        self.label_IP = gtk.Label("IP ADDRESS")
        self.label_IP.set_markup('<span color="blue"><b>MMFE8\nIP ADDRESS</b></span>')
        self.label_IP.set_justify(gtk.JUSTIFY_CENTER)
        self.combo_IP = gtk.combo_box_new_text()
        for i in range (len(self.ipAddr)):
            self.combo_IP.append_text(self.ipAddr[i]) 

        self.combo_IP.set_active(0)
        self.combo_IP.connect("changed",self.set_board_ip, self.entry_mmfeID) 

        self.combo_display = gtk.combo_box_new_text()
        for i in range(32):
            self.combo_display.append_text(str(hex(i)))
        self.combo_display.connect("changed",self.set_display)
        self.combo_display.set_active(0)


        #self.combo_vmm2_id = gtk.combo_box_new_text()
        #for i in range(256):
        #    self.combo_vmm2_id.append_text(str(hex(i)))

        #self.combo_vmm2_id.append_text("ALL")
        #self.combo_vmm2_id.set_active(0)
        #self.combo_vmm2_id.connect("changed",self.set_vmm_cfg_num)

        self.button_setIDs = gtk.Button("Set IDs")
        self.button_setIDs.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_setIDs.set_size_request(-1,-1)        
        self.button_setIDs.connect("clicked",self.set_IDs)
        
        self.label_mmfe8_id = gtk.Label("mmfe8")
        self.label_mmfe8_id.set_markup('<span color="blue"><b>mmfe8 ID</b></span>')
        self.label_mmfe8_id.set_justify(gtk.JUSTIFY_CENTER)
        self.label_Space20 = gtk.Label("   ")
        self.box_mmfeID = gtk.HBox()
        self.box_mmfeID.pack_start(self.label_mmfe8_id,expand=True)
        self.box_mmfeID.pack_start(self.entry_mmfeID,expand=False)

        self.label_display_id = gtk.Label("vmm2")
        self.label_display_id.set_markup('<span color="blue"><b>Scope  </b></span>')
        self.label_display_id.set_justify(gtk.JUSTIFY_CENTER)

        self.label_Space21 = gtk.Label("    ")
        self.box_labelID = gtk.HBox()
        self.box_labelID.pack_start(self.label_Space20,expand=True) #
        #self.box_labelID.pack_start(self.label_Space21,expand=False)
        #self.box_labelID.pack_start(self.label_vmm2_id,expand=False)
        #self.box_labelID.pack_start(self.qs_table,expand=False)

        self.label_Space22 = gtk.Label("  ") 

        self.box_ResetID = gtk.VBox()
        self.box_ResetID.pack_start(self.label_vmmGlobal_Reset,expand=False)
        self.box_ResetID.pack_start(self.vmmReset_table1,expand=False)
        self.box_ResetID.pack_start(self.button_resetVMM,expand=False)
        #self.box_ResetID.pack_start(self.label_Space22,expand=False)   

        self.box_ReadoutMask = gtk.VBox()
        self.box_ReadoutMask.pack_start(self.label_vmmReadoutMask,expand=False)
        self.box_ReadoutMask.pack_start(self.vmmReadout_table1,expand=False)
        #self.box_ResetID.pack_start(self.button_resetVMM,expand=False)
        #self.box_ResetID.pack_start(self.label_Space22,expand=False)   

        self.box_vmmID = gtk.HBox()
        self.box_vmmID.pack_start(self.button_setIDs,expand=False) #
        self.box_vmmID.pack_start(self.label_Space21,expand=True)
        self.box_vmmID.pack_start(self.label_display_id,expand=False)
        self.box_vmmID.pack_start(self.combo_display,expand=False)

        self.box_internal_trigger = gtk.HBox()
        self.box_internal_trigger.pack_start(self.label_internal_trigger,expand=False) #
        self.box_internal_trigger.pack_start(self.button_internal_trigger,expand=True)



        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        #                          FRAME 1   
        #
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


        self.frame_Reset = gtk.Frame()
        self.frame_Reset.set_shadow_type(gtk.SHADOW_OUT)
        self.frame_Reset.add(self.box_ResetID)

        self.frame_ReadoutMask = gtk.Frame()
        self.frame_ReadoutMask.set_shadow_type(gtk.SHADOW_OUT)
        self.frame_ReadoutMask.add(self.box_ReadoutMask)

        self.box_buttons = gtk.VBox()
        self.box_buttons.set_spacing(5)
        self.box_buttons.set_border_width(5)
        self.box_buttons.set_size_request(-1,-1)
        self.box_buttons.pack_start(self.label_But_Space9,expand=True)
        self.box_buttons.pack_start(self.label_IP,expand=False)
        self.box_buttons.pack_start(self.combo_IP,expand=False)
        self.box_buttons.pack_start(self.box_mmfeID,expand=False)
        #self.box_buttons.pack_start(self.box_labelID,expand=False)
        #self.box_buttons.pack_start(self.frame_configID,expand=False)
        self.box_buttons.pack_start(self.frame_ReadoutMask,expand=False)
        self.box_buttons.pack_start(self.box_vmmID,expand=False)
        self.box_buttons.pack_start(self.label_But_Space8,expand=True)  
        self.box_buttons.pack_start(self.button_print_config,expand=False)
        self.box_buttons.pack_start(self.button_write,expand=False)
        self.box_buttons.pack_start(self.label_But_Space3,expand=True)
        self.box_buttons.pack_start(self.frame_Reset,expand=False)  
        #self.box_buttons.pack_start(self.button_resetVMM,expand=False)
        self.box_buttons.pack_start(self.button_SystemInit,expand=False)
        self.box_buttons.pack_start(self.label_Space22,expand=True)
        self.box_buttons.pack_start(self.box_internal_trigger,expand=False)
        self.box_buttons.pack_start(self.box_pulses, expand=False)
        self.box_buttons.pack_start(self.label_pulses2, expand=False)
        self.box_buttons.pack_start(self.button_start,expand=False)
        #self.box_buttons.pack_start(self.button_start_no_cktp,expand=False)
        # self.box_buttons.pack_start(self.button_read_reg,expand=False)
        self.box_buttons.pack_start(self.label_But_Space4,expand=True)
        # self.box_buttons.pack_start(self.button_read_config_VMM_reg,expand=False)
        self.box_buttons.pack_start(self.button_read_XADC,expand=False)
        self.box_buttons.pack_start(self.label_But_Space5,expand=True)
        self.box_buttons.pack_start(self.button_exit,expand=False)                       
        self.box_buttons.pack_start(self.label_But_Space2,expand=True)
        self.box_buttons.pack_start(self.label_But_Space1,expand=True)


        self.page1_box = gtk.HBox(homogeneous=0,spacing=0)      
        self.page1_box.pack_start(self.VMM[0].box_all_channels, expand=False)
        self.page1_box.pack_end(self.VMM[0].box_variables, expand=True)       
        self.page2_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page2_box.pack_start(self.VMM[1].box_all_channels, expand=False)
        self.page2_box.pack_end(self.VMM[1].box_variables, expand=True)                     
        self.page3_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page3_box.pack_start(self.VMM[2].box_all_channels, expand=False)
        self.page3_box.pack_end(self.VMM[2].box_variables, expand=True)  
        self.page4_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page4_box.pack_start(self.VMM[3].box_all_channels, expand=False)
        self.page4_box.pack_end(self.VMM[3].box_variables, expand=True)  
        self.page5_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page5_box.pack_start(self.VMM[4].box_all_channels, expand=False)
        self.page5_box.pack_end(self.VMM[4].box_variables, expand=True)   
        self.page6_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page6_box.pack_start(self.VMM[5].box_all_channels, expand=False)
        self.page6_box.pack_end(self.VMM[5].box_variables, expand=True)  
        self.page7_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page7_box.pack_start(self.VMM[6].box_all_channels, expand=False)
        self.page7_box.pack_end(self.VMM[6].box_variables, expand=True)  
        self.page8_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page8_box.pack_start(self.VMM[7].box_all_channels, expand=False)
        self.page8_box.pack_end(self.VMM[7].box_variables, expand=True)  
        #self.page9_box = gtk.HBox(homogeneous=0,spacing=0)

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #
    #                      START the GUI
    #
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        self.page1_scrolledWindow = gtk.ScrolledWindow()
        self.page1_viewport = gtk.Viewport()
        self.page1_viewport.add(self.page1_box)
        self.page1_scrolledWindow.add(self.page1_viewport)
        self.page2_scrolledWindow = gtk.ScrolledWindow()
        self.page2_viewport = gtk.Viewport()
        self.page2_viewport.add(self.page2_box)
        self.page2_scrolledWindow.add(self.page2_viewport)
        
        self.page3_scrolledWindow = gtk.ScrolledWindow()
        self.page3_viewport = gtk.Viewport()
        self.page3_viewport.add(self.page3_box)
        self.page3_scrolledWindow.add(self.page3_viewport)
        self.page4_scrolledWindow = gtk.ScrolledWindow()
        self.page4_viewport = gtk.Viewport()
        self.page4_viewport.add(self.page4_box)
        self.page4_scrolledWindow.add(self.page4_viewport)
        self.page5_scrolledWindow = gtk.ScrolledWindow()
        self.page5_viewport = gtk.Viewport()
        self.page5_viewport.add(self.page5_box)
        self.page5_scrolledWindow.add(self.page5_viewport)
        self.page6_scrolledWindow = gtk.ScrolledWindow()
        self.page6_viewport = gtk.Viewport()
        self.page6_viewport.add(self.page6_box)
        self.page6_scrolledWindow.add(self.page6_viewport)
        self.page7_scrolledWindow = gtk.ScrolledWindow()
        self.page7_viewport = gtk.Viewport()
        self.page7_viewport.add(self.page7_box)
        self.page7_scrolledWindow.add(self.page7_viewport)
        self.page8_scrolledWindow = gtk.ScrolledWindow()
        self.page8_viewport = gtk.Viewport()
        self.page8_viewport.add(self.page8_box)
        self.page8_scrolledWindow.add(self.page8_viewport)
        
        self.notebook.append_page(self.page1_scrolledWindow, self.tab_label_1)
        self.notebook.append_page(self.page2_scrolledWindow, self.tab_label_2)
        self.notebook.append_page(self.page3_scrolledWindow, self.tab_label_3)
        self.notebook.append_page(self.page4_scrolledWindow, self.tab_label_4)
        self.notebook.append_page(self.page5_scrolledWindow, self.tab_label_5)
        self.notebook.append_page(self.page6_scrolledWindow, self.tab_label_6)
        self.notebook.append_page(self.page7_scrolledWindow, self.tab_label_7)
        self.notebook.append_page(self.page8_scrolledWindow, self.tab_label_8)
        self.notebook.append_page(self.userRegs.userRegs_box, self.tab_label_9)

        #self.notebook.append_page(self.page9_box, self.tab_label_9)
        self.box_GUI = gtk.HBox(homogeneous=0,spacing=0)
        #self.box_GUI.pack_start(self.myBigButtonsBox, expand=False)
        self.box_GUI.pack_start(self.box_buttons, expand=False)
        self.box_GUI.pack_end(self.notebook, expand=True)               
        #self.window.add(self.box_buttons)
        self.window.add(self.box_GUI)
        self.window.show_all()
        self.window.connect("destroy",self.destroy)

############################__INIT__################################
############################__INIT__################################

    def main(self):
        gtk.main()

############################################################
############################################################
##################      MAIN       #########################
############################################################
############################################################

if __name__ == "__main__":
    mmfe8 = MMFE8()
    mmfe8.main()

