#! /usr/bin/python
# -*- coding:utf-8 -*-
#--------------------------------------------------
#  sig monitor for DF91
#
# Author: Jia Tong from BJ SW Test
# Last updated: 6/9/2017
#--------------------------------------------------

import sys
import socket
import struct
import binascii
import time
import random
import subprocess
import threading

SEVER_ADDRESS = ('10.75.94.46', 2001) # 10.75.126.187
#CLIENT_ADDRESS = ('10.75.75.144', 2001) # ('10.75.48.61', 2001)

STRING_OK = "OK"
#event = threading.Event()

class SigSim():
	def __init__(self):
		self.BSimulationRunning = True
		self.BSimulationMaxNum = 100000
		self.sock = None
		self.msg_count = 0

		self.speedMotorRR_PTC = 0
		self.speedMotorRL_PTC = 1
		self.speedMotorFront_PTC = 2
		self.torqueActualRR_PTC = 3
		self.torqueActualRL_PTC = 4
		self.torqueActualFront_PTC = 5
		self.iPack2_BPG  = 6
		self.vDCLink2_BPG = 7
		self.vehicleSpeed_ESP = 1000

	def IncInt(self, a, step, max):
		if step >= 0:
			return (a+step) if a < (max-step) else 0
		else:
			return (a+step) if a > (0-step) else max
		
	def IncMySigs(self, step):
		self.speedMotorRR_PTC = self.IncInt(self.speedMotorRR_PTC, step, 0xFFFF)
		self.speedMotorRL_PTC = self.IncInt(self.speedMotorRL_PTC, step, 0xFFFF)
		self.speedMotorFront_PTC = self.IncInt(self.speedMotorFront_PTC, step, 0xFFFF)
		self.torqueActualRR_PTC = self.IncInt(self.torqueActualRR_PTC, step, 0x7FF)
		self.torqueActualRL_PTC = self.IncInt(self.torqueActualRL_PTC, step, 0x7FF)
		self.torqueActualFront_PTC = self.IncInt(self.torqueActualFront_PTC, step, 0x7FF)
		self.iPack2_BPG = self.IncInt(self.iPack2_BPG, step, 0xFFFF)
		self.vDCLink2_BPG = self.IncInt(self.vDCLink2_BPG, step, 0xFFFF)
		self.vehicleSpeed_ESP = self.IncInt(self.vehicleSpeed_ESP, step*100, 0xFFFF)
		
	def connect(self):
		# Create a UDP socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.sock.bind(CLIENT_ADDRESS);
		# Send data
		print >>sys.stderr, "\nTo server: ", SEVER_ADDRESS
		
	def send_msg_with_packed_data (self, packedData):
		#print >>sys.stderr, 'sending "%s"' % binascii.hexlify(packedData)
		self.sock.sendto(packedData, SEVER_ADDRESS)
		#print >>sys.stderr, sys.byteorder

	def send_msg (self, unMsgID, usMsgLen, llMsgContent):
		packed_data = struct.pack('>I', unMsgID) + struct.pack('>I', usMsgLen) + struct.pack('>Q', llMsgContent)
		self.send_msg_with_packed_data (packed_data)

	def send_msg_2 (self, unMsgID, usMsgLen, lMsgCnt1, lMsgCnt2): # DLC <= 8
		packed_data = struct.pack('>I', unMsgID) + struct.pack('>I', usMsgLen) + struct.pack('>I', lMsgCnt1) + struct.pack('>I', lMsgCnt2)
		self.send_msg_with_packed_data (packed_data)
		
	def send_msg_3 (self, unMsgID, usMsgLen, lMsgCnt1, lMsgCnt2, lMsgCnt3):  # DLC = 10
		packed_data = struct.pack('>I', unMsgID) + struct.pack('>I', usMsgLen) + struct.pack('>I', lMsgCnt1) + struct.pack('>I', lMsgCnt2) + struct.pack('>I', lMsgCnt3)
		self.send_msg_with_packed_data (packed_data)

	def calc_MotLSB_startbit(self, start_bit, bit_length):
		if(start_bit < 0 or start_bit > (20*8-1) or bit_length < 1 or bit_length > 64):
			print 'bad start_bit = %d' % (start_bit, bit_length)
			return -100
			
		l2r_bit = (start_bit / 8) * 8 + 8 - (start_bit % 8) # transfer MOT LSB bit to lef-to-right-order bit 
		l2r_bit -= (bit_length - 1)  # minus the offset
		r2l_bit = (l2r_bit / 8) * 8  + 8 - (l2r_bit % 8) # restore it back to MOT LSB bit from lef-to-right-order bit 
		
		return r2l_bit
	
	def set_sig_value(self, sig_name, start_bit, bit_length, sig_value):
		#decode it from 
		pass
	
	def send_all_my_sigs(self, step):
		self.msg_count += 1
		print '\n---send_count=#%06d---' % (self.msg_count)
		
		#PTC_EmotorStatus -- chassis
		# 1-2               3-4               5-6
		#torqueActualFront_PTC torqueActualRL_PTC torqueActualRR_PTC
		self.send_msg_2(0x440026, 8, (self.torqueActualFront_PTC << 21) + (self.torqueActualRL_PTC << 5), self.torqueActualRR_PTC << 21)
		print 'torqueActualRR_PTC=%d\ntorqueActualRL_PTC=%d\ntorqueActualFront_PTC=%d' % (self.torqueActualRR_PTC, self.torqueActualRL_PTC, self.torqueActualFront_PTC)
		
		#BPG_Msec100  -- gateway_ethernet
		#iPack2_BPG vDCLink2_BPG 
		self.send_msg_3(0x111, 11, (self.iPack2_BPG >> 8) & 0xFF, ((self.iPack2_BPG << 24) & 0xFF000000) + ((self.vDCLink2_BPG << 8) & 0xFFFF00), 0)
		print 'vDCLink2_BPG=%d[%f]\niPack2_BPG=%d[%f]' % (self.vDCLink2_BPG, 0.00762939453125 * self.vDCLink2_BPG + 0, self.iPack2_BPG, 0.1 * self.iPack2_BPG + 0)
		
		#PTC_EmotorSpeed -- chassis
		#speedMotorRR_PTC speedMotorRR_PTC speedMotorRL_PTC
		self.send_msg_2(0x440025, 8, (self.speedMotorFront_PTC << 16) + self.speedMotorRR_PTC, (self.speedMotorRL_PTC << 16)) 
		print 'speedMotorRR_PTC=%d\nspeedMotorRL_PTC=%d\nspeedMotorFront_PTC=%d' % (self.speedMotorRR_PTC, self.speedMotorRL_PTC, self.speedMotorFront_PTC)
		
		#ESP_VehicleSpeed -- chassis
		#vehicleSpeed_ESP
		self.send_msg_2(0x440208, 0x4, (self.vehicleSpeed_ESP << 16), 0)
		print 'vehicleSpeed_ESP=%d[%f]' % (self.vehicleSpeed_ESP, 0.01 * self.vehicleSpeed_ESP + 0)
		
		#
		self.IncMySigs(1)

	def run_sim(self):
		self.connect()
		
		if self.sock is None:
			print 'no socket connection is established.'
			return
			
		count = 0
		while self.BSimulationRunning:
			if count >= self.BSimulationMaxNum:
				print 'meet max num(%d) of simuation' % count
				break
				
			time.sleep(1)
			self.send_all_my_sigs(1)
			count += 1
	
	def stop(self):
		self.BSimulationRunning = False

ss = SigSim()

#print ss.calc_MotLSB_startbit(32, 16)
#print ss.calc_MotLSB_startbit(48, 16)
	
t1 = threading.Thread(target=ss.run_sim)
t1.start()

try:
	while True:
		time.sleep(1)
except KeyboardInterrupt as e:
	print('exit from keyborad interrupt')
	ss.stop()
		
t1.join()


print 'exit'
