#!/usr/bin/env python

import InstrumentDriver
from VISA_Driver import VISA_Driver
import visa
from InstrumentConfig import InstrumentQuantity

__version__ = "0.0.1"

class Error(Exception):
    pass

class Driver(VISA_Driver):
    """ This class implements the Rigol DSG3000 driver"""
  
    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # calling the generic VISA open to make sure we have a connection
        VISA_Driver.performOpen(self, options=options)
        

    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""
        self.log("Quantity to be retrieved is " + str(quant.name))
        if quant.name in('Ch1 - Data', 'Ch2 - Data', 'Ch3 - Data', 'Ch4 - Data'):
            self.log("Quantity is a channel data")
            channel = int(quant.name[2])
            value = self.get_channel_data(channel, quant)
        else:
            self.log("Quantity is not a channel data")
            value = VISA_Driver.performGetValue(self, quant, options)
        return value


    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the set value operation"""
        # check type of quantity
        self.log("Quantity is" + str(quant.name))
        if quant.name == "# of points":
            self.log ("# of points is" + str(value))
            value = int(value)
            self.log("After conversion is" + str(value))
            self.write(":WAV:POIN %d" %value)
        else:
            value = VISA_Driver.performSetValue(self, quant, value, sweepRate, options)
        return value

    def get_channel_data(self, channel, quant):
        """ Obtains data from channel
                - channel: channel whose data wants to be obtained
                - quant: data info
        """
        self.log("Now we are with channel " + str(channel))
        if self.getValue('Ch%d - Enabled' % channel):
            self.log("Channel is enabled")

            self.writeAndLog(':WAV:SOUR CHAN%d' %channel)
            raw_data = self.askAndLog(':WAV:DATA?')
            # raw_data is in string format
            # First, the string is converted into an array
            # The last value, which is empty, is discarted
            # Finally it is converted into a float

            self.log("Raw Data retrieved is " + str(raw_data))
            list_data = raw_data.split(",")
            list_data = list_data[:(len(list_data)-1)]
            vData = [float(i) for i in list_data]

            # Finally, the trace containing the x info is returned
            dt = float(self.ask(':WAV:XINC?'))
            value = quant.getTraceDict(vData, dt = dt)
        else: 
            self.log("Channel is not enabled")
            value = quant.getTraceDict([])
        return value
        
if __name__ == '__main__':
    pass
