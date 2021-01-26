// OPCR.h

// Date: 2/27/2020
// Version: 4.7.4, 64-bit
// Company: Optiphase, a Halliburton Service
// Author: John Dailing, john.dailing@halliburton.com

// Description:
// opcr.dll provides the functionality to control Optiphase interrogators that use the WTG (Waveform and Timing Generator) Controller,
// which includes CRI-X(undefined), CR1P, CR3P, CRI-3100, CRI-3200, CRI-3300, CRI-2200P1, CRI-4200P1, CR-4200, CRI-4400, CRI-4200M, CRI-4400M, and CRI-6200 interrogator instruments.
// For opcr.dll to function properly, it must have the file okFrontPanel.dll in the same directory.
// opcr.dll loads okFrontPanel.dll v4.3.1 which uses the Opal Kelly driver to communicate with the Opal Kelly controller in the instrument.
// The Opal Kelly driver, FrontPanelUSB-DriverOnly-4.3.1.exe, must be installed on the user PC. This driver or newer is needed for Windows 10.
// The Visual C++ redistribution, vcredist_x64.exe, must be installed on the user PC.

#ifndef _OPCR_H
#define _OPCR_H

typedef void* OPCR_HANDLE;
typedef int ErrorCode;

typedef int Bool;

typedef enum {
	opcr_NoError								=  0,
	opcr_driver_load_failed						= -1,
	opcr_invalid_function						= -2,
	opcr_invalid_handle							= -3,
	opcr_invalid_argument						= -4,
	opcr_out_of_range_argument					= -5,
	opcr_invalid_instrument						= -6,
	opcr_optical_rcvr_amp_communication_error	= -7,
	opcr_communication_error					= -8,
	opcr_optical_out_amp_communication_error	= -9,
	opcr_optical_amp_command_failed				= -10,
	opcr_optical_laser_communication_error		= -11,
	opcr_optical_laser_command_failed			= -12,
	opcr_safety_interlock_set					= -13,
	opcr_instrument_not_found					= -14,
	opcr_configuration_failed					= -15
} opcr__ErrorCode;
/*
Error Codes from Opal Kelly USB driver (-16 to -63):
	ok_Failed				= -16,
	ok_Timeout				= -17,
	ok_DoneNotHigh			= -18,
	ok_TransferError		= -19,
	ok_CommunicationError	= -20,
	ok_InvalidBitstream		= -21,
	ok_FileError			= -22,
	ok_DeviceNotOpen		= -23,
	ok_InvalidEndpoint		= -24,
	ok_InvalidBlockSize		= -25,
	ok_I2CRestrictedAddress	= -26,
	ok_I2CBitError			= -27,
	ok_I2CNack				= -28,
	ok_I2CUnknownStatus		= -29,
	ok_UnsupportedFeature	= -30

Error Codes from Laser communication (-64 to -127):
	OutOfRangeArgument					= -97
	InvalidCommandType					= -119	
	CommandTimeout						= -125	
	InvalidPacket						= -126
	InvalidCheckSum						= -127

	InvalidFirmwareUpdatePageCheckSum	= -102
	InvalidFirmwareUpdateFlashAddress	= -103
	InvalidFirmwareUpdateFlash			= -104	
	InvalidFirmwareUpdateErase			= -105	
	InvalidFirmwareUpdateCommit			= -106
	InvalidFirmwareUpdateSwitch			= -107	
*/

// All functions, return:
// 0, if no error.
// an error code from opcr_ErrorCode or one of the Opal Kelly USB driver error codes or Laser error codes, if error.

typedef enum {
	config_intclk						= 0,
	config_extclk_10MHz					= 1,
	config_extclk_25MHz					= 2,
	config_extclk_100MHz				= 3,
	config_extclk_25MHz_deskewed_minus	= 4, //not supported
	config_extclk_25MHz_deskewed		= 5,
	config_extclk_25MHz_deskewed_plus	= 6, //not supported
	config_extclk_100MHz_deskewed_minus	= 7, //not supported
	config_extclk_100MHz_deskewed		= 8,
	config_extclk_100MHz_deskewed_plus	= 9, //not supported
} opcr_config;

typedef enum {
	clk1_static_low		= 0,
	clk1_5MHz			= 1,
	clk1_6p25MHz		= 2,
	clk1_10MHz			= 3,
	clk1_12p5MHz		= 4,
	clk1_25MHz			= 5,
	clk1_50MHz			= 6,
	clk1_100MHz			= 7,
} clk1_select;

typedef enum {
	clk2_25MHz		= 0,
	clk2_100MHz		= 1,
} clk2_select;

typedef enum {
	short_delay			= 0,
	medium_delay		= 1,
	long_delay			= 2,
	extra_long_delay	= 3,
} coil_delay;

// Installed Instrument Options read from Instrument Flash.
struct InstrumentOptions {
	int controller_generation;
	int optical_rcvr_amp_ctrl;
	int optical_rcvr_dither;
	int electronic_rcvr_amp_ctrl;
	int eo_rcvr_type;
	int laser1_type;
	int laser2_type;
	int optical_out_amp_type;
	int compensator_type;
	int filter_type;
	int optical_rcvr_shutter_ctrl;
	int optical_out_shutter_ctrl;
};

// Timing structure for accessing calibration timing used when instrument was calibrated and these values written to instrument flash.
struct CalTiming {
	double pulse_width_0;
	double pulse_width_1;
	double pulse_width_2;
	double pulse_width_3;
	double connector_delay;
	double out_shutter_width_0;
	double out_shutter_width_1;
	double out_shutter_width_2;
	double out_shutter_width_3;
	double out_shutter_delay;
};

__declspec (dllexport) ErrorCode List_Unopened_Instruments(char* unique_IDs, int* list_length);
// Finds all unopened interrogator instruments (up to 16) and writes their comma-delimited unique IDs to the string pointed to by unique_IDs.
// Writes the number of interrogator instruments found to the integer pointed to by list_length.
// unique_IDs must be a pre-allocated string of length 256 plus null terminator in order to hold up to 16 unique IDs.
// list_length must be a pre-allocated integer.
// A unique ID is comprised of the instrument model number, followed by an underscore, followed by the instrument serial number.
// unique IDs example: CRI-3200_B010,CRI-2200P1_A003,CRI-4200P1_A005,CRI-4200_A001,CRI-4400_A001
__declspec (dllexport) ErrorCode Open_Communication(OPCR_HANDLE* opcr_handle_out, const char* unique_ID);
// Writes the newly opened handle to the OPCR_HANDLE pointed to by opcr_handle_out, which must be pre-allocated.
// The handle is to be used for all other functions below.
// If connected to only one interrogator instrument, unique_ID can be an empty string; otherwise, use the unique_ID to open communication and return a handle for a specific instrument.
__declspec (dllexport) ErrorCode Get_Instrument_Info(OPCR_HANDLE opcr_handle, char* model_out, char* serial_number_out, struct InstrumentOptions* instrument_options_out, struct CalTiming* cal_timing_out);
// Reads the instrument model name, the serial number, the installed options, and the calibration timing from the instrument.
// This information can be read even if the Instrument is not initialized.
// model_out must be a pre-allocated string of length 32 plus the null terminator.
// serial_number_out must be pre-allocated and able to hold up to 32 characters plus the null terminator.
// instrument_options_out must be pre-allocated.
// cal_timing_out must be pre-allocated.
// optical_out_amp_type: 0 = 17 dBm EDFA, 1 = 23 dBm EDFA.
// optical_rcvr_control_option: 0 = No Current Control, 1 = Programmable Constant Current Control only, 2 = Programmable Constant and Ramped Current Control available.
// electronic_rcvr_control_option: 0 = No Gain Control, 1 = Programmable Constant Gain Control only, 2 = Programmable Constant and Ramped Gain Control available.
// Both optical_rcvr_control_option and electronic_rcvr_control_option will never be option 2 at the same time.
// If Optical Rcvr does not uses dither, optical_rcvr_dither_type = 0; if Optical Rcvr uses dither, optical_rcvr_dither_type = 1.
// Even if optical_rcvr_dither_type = 0, dither will still be available for testing; optical_rcvr_dither_type = 0 just means dither is not used by the rcvr during normal operation.
// The first controller generation is indicated with a one.
// If generation 1 controller is used by the instrument, the function will return the default values for installed laser1_type, laser2_type, compensator_type, filter_type, and e-o receiver_type.
// See API manual or interrogator user manual for description of laser1_type, laser2_type, compensator_type, filter_type, and e-o receiver_type.
// pulse_width_0 is the pulse width, in clocks (10ns/clk, ~1m/clk) used during calibration
// For instruments with 4 selectable delay coils, pulse_width_0 thru pulse_width3 are the pulse widths used during calibration.
// Pulse widths can be 2 to 35 clocks (20 to 350ns).
// sample_delay is the delay in clocks (10ns/clk, ~1m/clk) that corresponds to location of fiber connector on instrument panel determined during calibration.
// Sample delay calibration parameter in flash can be 0 to 647.5 clocks (0 to 6.475µs).
// out_shutter_width_0 is the pulse width, in clocks (10ns/clk, ~1m/clk) used during calibration
// For instruments with 4 selectable delay coils, out_shutter_width_0 thru out_shutter_width_3 are the pulse widths used during calibration
// Output shutter width calibration parameter in flash can be 2 to 35 clocks (20 to 350ns).
// out_shutter_delay is the delay in clocks (10ns/clk, ~2m/clk), which is the delay used in calibration that opened the optical output shutter at the right time to allow the optical output pulse through.
// Output shutter delay calibration parameter in flash can be -128 to +127 clocks or -1280ns to +1270ns.
__declspec (dllexport) ErrorCode Is_Instrument_Initialized(OPCR_HANDLE opcr_handle, Bool* initialized_out, opcr_config* config_out, int* fw_ver_major, int* fw_ver_minor, int* fw_ver_patch);
// The instrument must be initialized every time instrument power is turned off and turned back on.
// Checks if instrument is initialized and to what configuration it is initilaized and what firmware version.
// Writes TRUE(1) or FALSE(0) to the Bool(int) pointed to by initialized_out, which must be pre-allocated
// Writes FPGA firmware version to the integers pointed to by fw_ver_major, fw_ver_minor, fw_ver_patch, which must be pre-allocated
// config_intclk indicates the FPGA is configured to use the controller internal clock to generate the 100MHz controller system clock, programmable reference clock out (typ 100MHz), and fixed 25MHz clock out.
// config_extclk_10MHz indicates the FPGA is configured to use an external 10MHz reference clock to generate the 100MHz controller system clock, programmable ref clock out (typ 100MHz), and fixed 25MHz clock out.
// config_extclk_25MHz indicates the FPGA is configured to use an external 25MHz reference clock to generate the 100MHz controller system clock, programmable ref clock out (typ 100MHz), and fixed 25MHz clock out.
// config_extclk_25MHz_deskewed indicates the FPGA is configured to use an external 25MHz reference clock and loop cable for deskewing to generate the 100MHz controller system clock, programmable ref clock out (typ 100MHz), and fixed 25MHz clock out.
// config_intclk, config_extclk_10MHz, config_extclk_25MHz, or config_extclk_100MHz are for a stand-alone interrogator or for the most upstream/master interrogator when interrogators are combined into a single fiber sensor.
// config_extclk_25MHz_deskewed is for all downstream interrogators when interrogators are combined into a single fiber sensor.
// When interrogators are combined into a single fiber sensor,
	// the most upstream/master interrogator is started via the Start_Timing function, and it outputs a start signal to the neighboring downstream interrogator,
	// who receives the start signal and passes it to the next neighboring downstream interrogator, and so on, for up to four interrogator instruments total.
	// The start signal daisy chain synchronizes the timing of all interrogator instruments, which includes the optical pulse timing.
	// A 25MHz clock signal is also daisy-chained in the same manner as the start signal.
	// Before the most upstream/master interrogator is started via the Start_Timing function, all downstream interrogator instruments should be external start enabled via the
	// Enable_External_Start_Timing function, and the start delays for each interrogator instrument should be properly set by using the Set_Timing_Start_Delay function.
__declspec (dllexport) ErrorCode Initialize_Instrument(OPCR_HANDLE opcr_handle, opcr_config config);
// The instrument must be initialized every time instrument power is turned off and turned back on.
// Loads instrument FPGA configuration indicated by the function argument config.
// The four available configurations differ in the clocking scheme used, for example whether the instrument’s internal clock is the clock source for the interrogator instrument or
// an external reference clock is the clock source for the interrogator instrument.
// Once the FPGA configures, the rest of the function turns on a 100MHz Reference Clock, sets optical pulsing (Timing) off, and sets instrument parameters to valid power on values.
// Once the Intialize Instrument function completes successfully, the remaining valid API functions can be used.
// If the function returns an opcr_optical_amp_communication_error (-9) error, then the FPGA configuration and the rest of Initialization was completed successfully, but
// the Output (Booster) EDFA communication failed when attempted as part of initialization.
// If the function returns an opcr_optical_amp_communication_error (-7) error, then the FPGA configuration and the rest of Initialization was completed successfully, but
// the Rcvr (Preamp) EDFA communication failed when attempted as part of initialization.
// These errors also occur if EDFA or its communication is not installed.
// Turns Reference Clock on and to default 100MHz.
// After function is called,
	// Timing will be off, which means no optical pulsing output at fiber sensor connector nor Sample Trigger output, and LVDS0 and TTL2 pulses will be disabled.
	// Pulses for all outputs listed below in Timing Parameters will be Disabled after Initialize_Instrument function completes,
	// except for CMOS1 Pulse Enable if Ouput Shutter installed and valid width and delay values loaded from flash.
	// Timing Parameters:
		// pulse_period will be 10000 clocks for 10KHz pulse rep rate.
		// pulse_width will be written to valid value based on calibration timing in flash or to 2 clocks, 20ns.
		// sample_delay will be written to 0 clocks, 0ns.

		// out_shutter_width (if applicable) will be initialized to a valid value based on calibration timing in flash or to 12 clocks, 120ns. // best guess for 2m optical pulse
		// out_shutter_delay (if applicable) will be initialized to a valid value based on calibration timing in flash or to -8 clocks, -80ns. // most common working setting so far
		// cmos0_width (if no out_shutter) will be initialized to 10 clocks, 120ns.
		// cmos0_delay (if no out_shutter) will be initialized to 0 clocks, 0ns.

		// rcvr_shutter_width_0 (if applicable) will be initialized to 12 clocks, 120ns. // best guess for 2m optical pulse into 5m delay coil
		// For Dual Wavelength Instruments, like CRI-4400, rcvr_shutter_width_0 (if applicable) will be initialized to 32 clocks, 320ns.
		// rcvr_shutter_delay_0 (if applicable) will be initialized to a valid value based on connector_delay in calibration timing in flash + 50 clocks or to 150 clocks, 1500ns.
		// cmos1_width_0 (if no rcvr_shutter) will be initialized to 10 clocks, 100ns.
		// cmos1_delay_0 (if no rcvr_shutter) will be initialized to 0 clocks, 0ns.

		// rcvr_shutter_width_1 (if applicable) will be initialized to 16 clocks, 160ns. // best guess for 6m optical pulse into 15m delay coil
		// For Dual Wavelength Instruments, like CRI-4400, rcvr_shutter_width_1 (if applicable) will be initialized to 36 clocks, 360ns.
		// rcvr_shutter_delay_1 (if applicable) will be initialized to a valid value based on rcvr_shutter_delay_0 + 50 clocks, 500ns.
		// cmos1_width_1 (if no rcvr_shutter) will be initialized to 10 clocks, 100ns.
		// cmos1_delay_1 (if no rcvr_shutter) will initialized to 0 clocks, 0ns.

		// rcvr_shutter_width_2 (if applicable) will be initialized to 20 clocks, 200ns. // best guess for 10m optical pulse into 25m delay coil
		// For Dual Wavelength Instruments, like CRI-4400, rcvr_shutter_width_2 (if applicable) will be initialized to 40 clocks, 400ns.
		// rcvr_shutter_delay_2 (if applicable) will be initialized to a valid value based on rcvr_shutter_delay_1 + 50 clocks, 500ns.
		// cmos1_width_2 (if no rcvr_shutter) will be initialized to 10 clocks, 100ns.
		// cmos1_delay_2 (if no rcvr_shutter) will be initialized to 0 clocks, 0ns.

		// rcvr_shutter_width_3 (if applicable) will be initialized to 26 clocks, 260ns. // best guess for 16m optical pulse into 40m delay coil
		// For Dual Wavelength Instruments, like CRI-4400, rcvr_shutter_width_0 (if applicable) will be initialized to 46 clocks, 460ns.
		// rcvr_shutter_delay_3 (if applicable) will be initialized to a valid value based on rcvr_shutter_delay_2 + 50 clocks, 500ns.
		// cmos1_width_3 (if no rcvr_shutter) will be initialized to 10 clocks, 100ns.
		// cmos1_delay_3 (if no rcvr_shutter) will be initialized to 0 clocks, 0ns.

		// cmos2_width (if no out_shutter) will be initialized to 10 clocks, 100ns.
		// cmos2_delay (if no out_shutter) will be initialized to 0 clocks, 0ns.

		// cmos3_width (if no out_shutter) will be initialized to 10 clocks, 100ns.
		// cmos3_delay (if no out_shutter) will be initialized to 0 clocks, 0ns.

		// lvds1_width (if no out_shutter) will be initialized to 10 clocks, 100ns.
		// lvds1_delay (if no out_shutter) will be initialized to 0 clocks, 0ns.
	// Optical Output Amp will be off.
	// Optical Rcvr Amp will be off (if applicable).
	// Optical Rcvr Dither will be off with default Optical Rcvr Dither amplitude of 1.2V.
 	// Electronic Rcvr Amp Gain will be 0.0dB (if applicable).
	// Ramped Optical Rcvr Amp Current will be 0mA (if applicable). 
	// Ramped Electronic Rcvr Amp Gain will be 0.0dB (if applicable).
	// Modulation Ramp will be off (if applicable).
	// Polarity Switching will be off (if applicable).
// If Close_Communication is called and instrument stays powered on and a new Open_Communication is called, there is no need to call Initialize_Instrument.
// Use config_intclk to configure the controller to use its internal clock to generate the 100MHz controller system clock, programmable reference clock out (typ 100MHz), and fixed 25MHz clock out.
// Use config_extclk_10MHz to configure the controller to use an external 10MHz reference clock to generate the 100MHz controller system clock, programmable ref clock out (typ 100MHz), and fixed 25MHz clock out.
// Use config_extclk_25MHz to configure the controller to use an external 25MHz reference clock to generate the 100MHz controller system clock, programmable ref clock out (typ 100MHz), and fixed 25MHz clock out.
// Use config_extclk_25MHz_deskewed to configure the controller to use an external 25MHz reference clock and loop cable for deskewing to generate the 100MHz controller system clock, programmable ref clock out (typ 100MHz), and fixed 25MHz clock out.
// config_intclk, config_extclk_10MHz, config_extclk_25MHz, or config_extclk_100MHz are for a stand-alone interrogator or for the most upstream/master interrogator when interrogators are combined into a single fiber sensor.
// config_extclk_25MHz_deskewed is for all downstream interrogators when interrogators are combined into a single fiber sensor.
// When interrogators are combined into a single fiber sensor,
	// the most upstream/master interrogator is started via the Start_Timing function, and it outputs a start signal to the neighboring downstream interrogator,
	// who receives the start signal and passes it to the next neighboring downstream interrogator, and so on, for up to four interrogator instruments total.
	// The start signal daisy chain synchronizes the timing of all interrogator instruments, which includes the optical pulse timing.
	// A 25MHz clock signal is also daisy-chained in the same manner as the start signal.
	// Before the most upstream/master interrogator is started via the Start_Timing function, all downstream interrogator instruments should be external start enabled via the Enable_External_Start_Timing function, and
	// the start delays for each interrogator instrument should be properly set by using the Set_Timing_Start_Delay function.

__declspec (dllexport) ErrorCode Get_Controller_Status_Reg(OPCR_HANDLE opcr_handle, int status_register, int* status);
// Reads the WTG Controller status register indicated by status_register and writes its value to the integer pointed to by status pointer.
// status must be pre-allocated.
// Status Registers 0 through 7 can be read.
// Refer to the OPCR API user manual for a description of the WTG Controller Status Registers.
__declspec (dllexport) ErrorCode Get_Controller_Temperature(OPCR_HANDLE opcr_handle, double* celsius);
// Controller Temperature is not valid on instruments that use WTG Controller Gen1, and it does return and opcr_invalid_function error if called.
// Controller Temperature is valid on instruments that use WTG Controller Gen2 or later.
// Gets the WTG Controller temperature and writes that temperature to the double pointed to by celsius pointer.
// celsius must be pre-allocated.
// The temperature sensors range is -55C to +125C.
// The controller temperature runs hotter than internal environment temperature and external environment temperature.
// At 25C external environment temperature and 30.5C internal air temperature near WTG Controller, the WTG Controller PCB reads 42C on CRI-4200 interrogator instruments.

__declspec (dllexport) ErrorCode Get_Reference_Clock(OPCR_HANDLE opcr_handle, Bool* is_on, clk1_select* select);
// Gets the Reference Clock (Clock 1) output state of static low or a 5MHz, 6.25MHz, 10MHz, 12.5MHz, 25MHz, 50MHz, or 100MHz.
// is_on is TRUE if Reference Clock (Clock 1) is on. is_on must be pre-allocated. 
// select indicates the Reference Clock (Clock 1) selection, and select must be pre-allocated.
__declspec (dllexport) ErrorCode Set_Reference_Clock(OPCR_HANDLE opcr_handle, clk1_select select);
// The Initialize_Instrument function turns Reference Clock (Clock 1) output on and to default 100MHz, select = 7.
// Sets the Reference Clock (Clock 1) output to static low or a frequency of 5MHz, 6.25MHz, 10MHz, 12.5MHz, 25MHz, 50MHz, or 100MHz..
// The Reference Clock (Clock 1) is a 5V CMOS output.
// Once the instrument is initialization, the Reference Clock (Clock 1) output is off only if manually turned off or if Close_Communication_and_Instrument_Off 
// was previously called and then a new Open_Communication is called and Initialize_Instrument is not called because the instrument is already initialized.

__declspec (dllexport) ErrorCode Get_Clock_1(OPCR_HANDLE opcr_handle, Bool* is_on, clk1_select* select);
__declspec (dllexport) ErrorCode Set_Clock_1(OPCR_HANDLE opcr_handle, clk1_select select);
// same functions as above and controls the same reference clock (Clock 1) output out of the interrogator

__declspec (dllexport) ErrorCode Get_Clock_2(OPCR_HANDLE opcr_handle, clk2_select* select);
// Gets the Clock 2 output frequency of 25MHz (select = 0) or 100MHz (select = 1).
// select indicates the Clock 2 selection, and select must be pre-allocated.
__declspec (dllexport) ErrorCode Set_Clock_2(OPCR_HANDLE opcr_handle, clk2_select select);
// Sets the Clock 2 output frequency to 25MHz (select = 0) or 100MHz (select = 1).
// The Clock 2 is a 5V CMOS output.
// All configurations initialize Clock 2 to 25MHz clock, except the Ext 100MHz configurations which intitalize Clock 2 to 100MHz. 

__declspec (dllexport) ErrorCode Is_Timing_Ext_Start_Enabled(OPCR_HANDLE opcr_handle, Bool* ext_start_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments.
// ext_start_en is written as TRUE if External Timing Start is enabled (via the Enable_External_Start_Timing function).
// ext_start_en must be pre-allocated.

__declspec (dllexport) ErrorCode Get_External_Start_Timing_Mode(OPCR_HANDLE opcr_handle, int* mode);
// mode is the External Start Modes and can be:
// 0) level mode for timing start and stop, or
// 1) edge mode for timing start only, or
// 2) or edge mode for timing stop only, or
// 3) or edge mode for timing start and stop
// mode must be pre-allocated.
__declspec (dllexport) ErrorCode Set_External_Start_Timing_Mode(OPCR_HANDLE opcr_handle, int mode);
// mode is the External Start Modes and can be:
// 0) level mode for timing start and stop, or
// 1) edge mode for timing start only, or
// 2) or edge mode for timing stop only, or
// 3) or edge mode for timing start and stop

__declspec (dllexport) ErrorCode Enable_External_Start_Timing(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments.
// Optical Pulse (LVDS0) pulse and Sample Trigger (TTL2) pulse, whose timing is set by Set_Timing_Basic or Set_Timing_CRI4200 functions, are enabled within the Enable_External_Start_Timing function.
// Used when interrogators are combined into a single fiber sensor, by all downstream interrogator instruments.
// When interrogators are combined into a single fiber sensor,
	// the most upstream/master interrogator is started via the Start_Timing function, and it outputs a start signal to the neighboring downstream interrogator,
	// who receives the start signal and passes it to the next neighboring downstream interrogator, and so on, for up to four interrogator instruments total.
	// The start signal daisy chain synchronizes the timing of all interrogator instruments, which includes the optical pulse timing.
	// A 25MHz clock signal is also daisy-chained in the same manner as the start signal.
	// Before the most upstream/master interrogator is started via the Start_Timing function, all downstream interrogator instruments should be external start enabled via the Enable_External_Start_Timing function, and
	// the start delays for each interrogator instrument should be properly set by using the Set_Timing_Start_Delay function.
// Once an interrogator instrument is external start enabled, it remains enabled until its Stop_Timing function is called, its Initialize_Instrument function is called, its Close_Communication_and_Instrument_Off
// function is called, its safety interlock is set, or its power is turned off; consequently, the downstream interrogators do not need Enable_External_Start_Timing re-issued between acquisition/timing cycles,
// which are started and stopped by issuing Start_Timing and Stop_Timing functions to only the most upstream/master interrogator.
// Optical Pulse (LVDS0) and Sample Trigger (TTL2), which are set by Set_Timing_Basic or Set_Timing_CRI4200 functions, are pulse enabled within the Enable_External_Start_Timing function.
// If the external safety interlock input is set, calling this function returns the opcr_safety_interlock_set error, and does not enable external start timing.
// The external safety interlock is set if it is left open or driven logic high.  If it is shorted to ground or driven low, the external safety interlock is cleared, and the interrogator can function normally.
// The external safety interlock input is a 3.3V CMOS input.  It is not 5V tolerant.
__declspec (dllexport) ErrorCode Disable_External_Start_Timing(OPCR_HANDLE opcr_handle);
// Used when interrogators are combined into a single fiber sensor, by all downstream interrogator instruments. (see function above for more detailed about combined interrogator operation)
// Disables the interrogator's Timing from starting via its external start input and stops the interrogator timing if running.
// Optical Pulse (LVDS0) pulse and Sample Trigger (TTL2) pulse, whose timing is set by Set_Timing_Basic or Set_Timing_CRI4200 functions, are disabled within the Disable_External_Start_Timing function.

__declspec (dllexport) ErrorCode Get_Timing_Start_Delay(OPCR_HANDLE opcr_handle, int* instrument_delay, int* fine_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments.
// Used when interrogators are combined into a single fiber sensor.
// see function below for more detail regarding combined interrogator operation.
__declspec (dllexport) ErrorCode Set_Timing_Start_Delay(OPCR_HANDLE opcr_handle, int instrument_delay, int fine_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments..
// Used when interrogators are combined into a single fiber sensor.
// When interrogators are combined into a single fiber sensor,
	// the most upstream/master interrogator is started via the Start_Timing function, and it outputs a start signal to the neighboring downstream interrogator,
	// who receives the start signal and passes it to the next neighboring downstream interrogator, and so on, for up to four interrogator instruments total.
	// The start signal daisy chain synchronizes the timing of all interrogator instruments, which includes the optical pulse timing.
	// A 25MHz clock signal is also daisy-chained in the same manner as the start signal.
	// Before the most upstream/master interrogator is started via the Start_Timing function, all downstream interrogator instruments should be external start enabled via the Enable_External_Start_Timing function, and
	// the start delays for each interrogator instrument should be properly set by using the Set_Timing_Start_Delay function.
// To properly set the start delays, the instrument_delay for each interrogator instrument should be set to a value equaling the number of interrogator instruments that are downstream that particular interrogator instrument.
// For example, if four instruments are daisy chained,
	// the most upstream/master instrument should have its instrument_delay set to 3,
	// the next downstream instrument should have its instrument_delay set to 2,
	// the next downstream instrument should have its instrument_delay set to 1,
	// the last downstream instrument should have its instrument_delay set to 0.
// For example, if two instruments are daisy chained,
	// the most upstream/master instrument should have its instrument_delay set to 1,
	// the downstream instrument should have its instrument_delay set to 0,
// The valid range for instrument_delay is 0 to 3.
// fine_delay is in units of "System Clock Cycles" (typically 10ns), and allows adjusting the timing of each interrogator instrument to compensate for fiber length mismatches that may exist.
// between instruments whose fiber has been combined into a single fiber sensor.  This also allows intentionally skewing the optical pulse from each instrument, if desired, so each instrument's pulse passes through the optical coupler at slightly different points in time.
// The valid range for fine_delay is 0 to 255.
// If the interrogator timing is running via a previous call to Start_Timing, then this function internal calls Stop_Timing, sets the delays, and then calls Start_Timing.

__declspec (dllexport) ErrorCode Is_Start_Timing_On(OPCR_HANDLE opcr_handle, Bool* sw_start);
// sw_start is written as TRUE if Timing is On (via the Start_Timing function).
// sw_start must be pre-allocated.
__declspec (dllexport) ErrorCode Start_Timing(OPCR_HANDLE opcr_handle);
// Starts all timing set by the Set_Timing_Basic or Set_Timing_CRI4200 functions.
// Optical Pulse (LVDS0) pulse and Sample Trigger (TTL2) pulse, whose timing is set by Set_Timing_Basic or Set_Timing_CRI4200 functions, are enabled within the Start_Timing function.
// Turns Reference Clock on, if not already on.
// Reference Clock would be off if manually turned off or if Close_Communication_and_Instrument_Off was previously called and then a new Open_Communication is called and Initialize_Instrument is not called because the instrument is already initialized.
// If the external safety interlock input is set, calling this function returns the opcr_safety_interlock_set error, and does not start timing.
// The external safety interlock is set if it is left open or driven logic high.  If it is shorted to ground or driven low, the external safety interlock is cleared, and the interrogator can function normally.
// The external safety interlock input is a 3.3V CMOS input.  It is not 5V tolerant on Gen2 WTG controller.  It is 5V tolerant on Gen3 or higher WTG controller.
// The timing stays on until Stop_Timing, Inititalize_Instrument, or Close_Communication_and_Instrument_Off is called or until the safety interlock is set or power is turned off.

__declspec (dllexport) ErrorCode Start_Timing_Without_Sample_Trigger(OPCR_HANDLE opcr_handle);
// Same as the Start_Timing function but the Sample Trigger is disabled within the function.

__declspec (dllexport) ErrorCode Is_Sample_Trigger_Enabled(OPCR_HANDLE opcr_handle, Bool* trigger_en);
// trigger_en is written as TRUE if the Sample Trigger is Enabled and as FALSE if it is not Enabled.
// trigger_en must be pre-allocated
// The Sample Trigger is Enabled when the functions Start_Timing, Enable_External_Start_Timing, or Enable_Sample_Trigger are called.
// The Sample Trigger is Disabled when the functions Stop_Timing, Disable_External_Start_Timing, Disable_Sample_Trigger, Start_Timing_Without_Sample_Trigger, Initialize_Instrument, and Close_Communication_and_Instrument_Off are called.

__declspec (dllexport) ErrorCode Enable_Sample_Trigger(OPCR_HANDLE opcr_handle);
// Enables Sample Trigger, so when Timing is on, the Sample Trigger pulses for 200ns, and usesthe Sample Trigger delay already set with the Set_Timing function.
// This function can be used if the Start_Timing_Without_Sample_Trigger function is used instead of the Start_Timing function.

__declspec (dllexport) ErrorCode Disable_Sample_Trigger(OPCR_HANDLE opcr_handle);
// Disables Sample Trigger, so even if Timing is on, the Sample Trigger will stay at its off logic level.

__declspec (dllexport) ErrorCode Stop_Timing(OPCR_HANDLE opcr_handle);
// Stop all timing, except reference clock(s).
// Optical Pulse (LVDS0) pulse and Sample Trigger (TTL2) pulse, whose timing is set by Set_Timing_Basic or Set_Timing_CRI4200 functions, are disabled within the Stop_Timing function.
// Also disables external start timing, if enabled.

__declspec (dllexport) ErrorCode Is_Timing_On(OPCR_HANDLE opcr_handle, Bool* timing_is_on);
// timing_is_on is written as TRUE if Timing is On (via the Start_Timing function or External Start).
// timing_is_on must be pre-allocated.
__declspec (dllexport) ErrorCode Get_Timing_Basic(OPCR_HANDLE opcr_handle, int* pulse_period, double* pulse_width, double* sample_delay);
// This function is applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments.
// For CRI-4200 and CRI-4400 interrogator instruments (or instruments with an output shutter), this function can be used in lieu of Set_Timing_CRI4200.
// pulse_period, pulse_width, sample_delay must be pre-allocated.
// See Set_Timing_Basic function below for more details.
__declspec (dllexport) ErrorCode Set_Timing_Basic(OPCR_HANDLE opcr_handle, int pulse_period, double pulse_width, double sample_delay);
// This function is applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments.
// For CRI-4200 and CRI-4400 interrogator instruments (or instruments with an output shutter),
// this function can be used in lieu of Set_Timing_CRI4200, to set optical pulse and sample delay timing with output shutter (and rcvr shutter) statically open, or
// this function can be used in lieu of Set_Timing_CRI4200, if output shutter is controlled by Set_Timing_Output_Shutter function.
// If output or rcvr shutter is installed, this function statically opens them.
// Provides access to the minimal, basic digital timing outputs, which is used for CR1P, CR3P, CRI-3100, CRI-3200, CRI-3300, CRI-2200P1, and CRI-4200P1 instruments.
// Sets the pulse period & width for the pulsed Optical Output and the delay for the 200nsec wide Sample Trigger for external Digitizer.
// pulse_period, pulse_width, and sample_delay are in units of "System Clock Cycles".
// The System Clock is 100MHz, so for example, a value of 25 = 25 x 10ns = 250ns.
// All delays represent the delay from leading edge of pulse to the leading edge of the associated parameter's pulse.
// pulse_period range is 500 to 65536. (200 KHz to 1526 Hz)
// pulse_width range is 1 to 35 and must be a multiple of 0.5, i.e. 1.0, 1.5, 2.0, 2.5, etc.
// sample_delay range is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5; i.e. 0.0, 0.5,1.0, 1.5, etc.
// The pulse invert is turned off and pulse disabled for CMOS0, CMOS1, CMOS2, CMOS3, and LVDS1.
// Turns Reference Clock on, if not already on.
// Reference Clock would be off if manually turned off or if Close_Communication_and_Instrument_Off was previously called and then a new Open_Communication
// is called and Initialize_Instrument is not called because the instrument is already initialized.
// If Timing is on when this function is called, it is momentarily turned off and then turned back on.
// The number of samples per pulse is not controlled by this API or the instrument; it is controlled by the external Digitizer, and it should not span a period larger than the pulse_period.
// If the interrogator timing is running via a previous call to Start_Timing, then this function internal calls Stop_Timing, sets the timing parameters, and then calls Start_Timing.
__declspec (dllexport) ErrorCode Get_Timing_CRI4200(OPCR_HANDLE opcr_handle, int* pulse_period, double* pulse_width, double* sample_delay, double* output_shutter_width, double* output_shutter_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments.
// pulse_period, pulse_width, sample_delay, output_shutter_width, output_shutter_delay, rcvr_shutter_width, and rcvr_shutter_delay must be pre-allocated.
// See Set_Timing_CRI4200 function below for more details.
__declspec (dllexport) ErrorCode Set_Timing_CRI4200(OPCR_HANDLE opcr_handle, int pulse_period, double pulse_width, double sample_delay, double output_shutter_width, double output_shutter_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments.
// Sets the pulse period & width for the pulsed Optical Output, the delay for the 200nsec wide Sample Trigger for external Digitizer, and Output Shutter Switch timing.
// pulse_period, pulse_width, sample_delay, output_shutter_width, and output_shutter_delay are in units of "System Clock Cycles".
// The System Clock is 100MHz, so for example, a value of 25 = 25 x 10ns = 250ns.
// All delays represent the delay from leading edge of pulse to the leading edge of the associated parameter's pulse.
// pulse_period range is 500 to 65536. (200 KHz to 1526 Hz)
// pulse_width range is 1 to 35 and must be a multiple of 0.5, i.e. 1.0, 1.5, 2.0, 2.5, etc.
// sample_delay range is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5; i.e. 0.0, 0.5,1.0, 1.5, etc.
// The output shutter signal comes from CMOS0.
// output_shutter_width is 2 to (pulse_period-2) and must be a multiple of 0.5, i.e. 2.0, 2.5, 3.0, 3.5, etc.
// output_shutter_delay is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5.
// output_shutter pulse invert is set properly based on optical_out_shutter_ctrl installed option.
// output_shutter enable is turned on.
// If rcvr shutter is installed, this function statically opens it.
// Turns Reference Clock on, if not already on.
// Reference Clock would be off if manually turned off or if Close_Communication_and_Instrument_Off was previously called and then a new Open_Communication
// is called and Initialize_Instrument is not called because the instrument is already initialized.
// If Timing is on when this function is called, it is momentarily turned off and then turned back on.
// The number of samples per pulse is not controlled by this API or the instrument; it is controlled by the external Digitizer, and it should not span a period larger than the pulse_period.
// If the interrogator timing is running via a previous call to Start_Timing, then this function internal calls Stop_Timing, sets the timing parameters, and then calls Start_Timing.

__declspec (dllexport) ErrorCode Get_Sample_Trigger_Count(OPCR_HANDLE opcr_handle, unsigned int* count);
// count is the 32bit number of SAmple Triggers output since the last Timing Start.
// count must be pre-allocated

__declspec (dllexport) ErrorCode Is_Output_Shutter_Pulse_Enabled(OPCR_HANDLE opcr_handle, Bool* pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments (or for instruments with output shutter indicated as an installed option).
// returns the state of the pulse enable in pulse_en, which must be pre-allocated.
__declspec (dllexport) ErrorCode Enable_Output_Shutter_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments (or for instruments with output shutter indicated as an installed option), but
// it should not be needed since Set_Timing_CRI4200 and Set_Timing_Output_Shutter functions enable the output shutter.
// Enables pulse of programmed width and delay to be output when Timing is started. Set_Timing_Output_Shutter function also enables the pulse.
__declspec (dllexport) ErrorCode Disable_Output_Shutter_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments (or for instruments with output shutter indicated as an installed option), but should not needed.
// Disables pulse from being output when Timing is started.
__declspec (dllexport) ErrorCode Get_Timing_Output_Shutter(OPCR_HANDLE opcr_handle, double* output_shutter_width, double* output_shutter_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// For the CRI-4200 or CRI-4400 interrogator instruments, this function can be used in lieu of Get_Timing_CRI4200 for reading the output shutter timing.
// pulse_period, output_shutter_width, and output_shutter_delay must be pre-allocated.
// Set_Timing_Output_Shutter function below for more details.
__declspec (dllexport) ErrorCode Set_Timing_Output_Shutter(OPCR_HANDLE opcr_handle, int pulse_period, double output_shutter_width, double output_shutter_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// For the CRI-4200 or CRI-4400 interrogator instruments, this function can be used in lieu of Set_Timing_CRI4200 for controlling the Output shutter.
// The output shutter signal comes from CMOS0.
// output_shutter_width range is 2 to (pulse_period-0.5) and must be a multiple of 0.5, i.e. 2.0, 2.5, 3.0, 3.5, etc.
// output_shutter_delay range is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5.
// pulse_period is only read by this function; use Set_Timing_Basic or Set_Timing_CRI4200 to set pulse_period.

__declspec (dllexport) ErrorCode Is_Rcvr_Shutter_Pulse_Enabled(OPCR_HANDLE opcr_handle, Bool* pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments (or for instruments with rcvr shutter indicated as an installed option).
// returns the state of the pulse enable in pulse_en, which must be pre-allocated.
__declspec (dllexport) ErrorCode Enable_Rcvr_Shutter_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments (or for instruments with rcvr shutter indicated as an installed option), but
// it should not be needed since Set_Timing_Rcvr_Shutter function enables the rcvr shutter.
// Enables pulse of programmed width and delay to be output when Timing is started. Set_Timing_Rcvr_Shutter function also enables the pulse.
__declspec (dllexport) ErrorCode Disable_Rcvr_Shutter_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments(or for instruments with rcvr shutter indicated as an installed option), but should not needed.
// Disables pulse from being output when Timing is started.
__declspec (dllexport) ErrorCode Is_Rcvr_Shutter_Individual_Pulse_Enabled(OPCR_HANDLE opcr_handle, int select, Bool* pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments.
// reads the individual pulse enable for pulse 0, 1, 2, or 3, as indicated by select, and writes to pulse_en, which must be pre-allocated.
__declspec (dllexport) ErrorCode Rcvr_Shutter_Individual_Pulse_Enable(OPCR_HANDLE opcr_handle, int select, Bool pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments.
// writes the individual pulse enable for pulse 0, 1, 2, or 3, as indicated by select, according to pulse_en. Set_Timing_Rcvr_Shutter function also enables the individual pulse selected.
__declspec (dllexport) ErrorCode Get_Timing_Rcvr_Shutter(OPCR_HANDLE opcr_handle, int select, double* rcvr_shutter_width, double* rcvr_shutter_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments.
// reads the individual width and delay for pulse 0, 1, 2, or 3, as indicated by select, and writes to rcvr_shutter_width and rcvr_shutter_delay, which must be pre-allocated.
__declspec (dllexport) ErrorCode Set_Timing_Rcvr_Shutter(OPCR_HANDLE opcr_handle, int pulse_period, int select, double rcvr_shutter_width, double rcvr_shutter_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, or CRI-4200P1 interrogator instruments.
// This function is applicable for the CRI-4200 or CRI-4400 interrogator instruments.
// Use this function to setup the four available receiver shutter pulses.
// writes the pulse width and delay for pulse 0, 1, 2, or 3, as indicated by select, according to pulse_en. Set_Timing_Rcvr_Shutter function also enables the individual pulse selected.
// rcvr_shutter_width range is 2 to (pulse_period-2) and must be a multiple of 0.5, i.e. 2.0, 2.5, 3.0, 3.5, etc.
// rcvr_shutter_delay range is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5.
// The receiver shutter signal comes from CMOS1.
// pulse_period is only read by this function; use Set_Timing_Basic or Set_Timing_CRI4200 to set pulse_period.

__declspec (dllexport) ErrorCode Is_CMOS0_Pulse_Enabled(OPCR_HANDLE opcr_handle, Bool* pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse enable in pulse_en, which must be pre-allocated.
__declspec (dllexport) ErrorCode Enable_CMOS0_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Enables pulse of programmed width and delay to be output when Timing is started.
__declspec (dllexport) ErrorCode Disable_CMOS0_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Disables pulse from being output when Timing is started. This makes CMOS0_On and CMOS0_Off functions valid.
__declspec (dllexport) ErrorCode Is_CMOS0_Pulse_Inverted(OPCR_HANDLE opcr_handle, Bool* inverted);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse invert in inverted, which must be pre-allocated.
__declspec (dllexport) ErrorCode CMOS0_Pulse_Invert(OPCR_HANDLE opcr_handle, Bool invert);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// sets the state of the pulse invert according to invert.
__declspec (dllexport) ErrorCode Get_Timing_CMOS0(OPCR_HANDLE opcr_handle, double* cmos0_width, double* cmos0_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// cmos0_width and cmos0_delay must be pre-allocated.
// Set_Timing_CMOS0 function below for more details.
__declspec (dllexport) ErrorCode Set_Timing_CMOS0(OPCR_HANDLE opcr_handle, int pulse_period, double cmos0_width, double cmos0_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Use this function to setup the CMOS0 pulse if not used as output shutter pulse.
// cmos0__width range is 2 to (pulse_period-2) and must be a multiple of 0.5, i.e. 2.0, 2.5, 3.0, 3.5, etc.
// cmos0__delay range is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5.
// pulse_period is only read by this function; use Set_Timing_Basic or Set_Timing_CRI4200 to set pulse_period.
__declspec (dllexport) ErrorCode Is_CMOS0_On(OPCR_HANDLE opcr_handle, Bool* logic_level);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the Output Logic Level CMOS0 in logic_level, which must be pre-allocated.
__declspec (dllexport) ErrorCode CMOS0_On(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if CMOS0 pulse is enabled.
// if CMOS0 pulse is disabled, sets the Output Logic Level of CMOS0 high.
__declspec (dllexport) ErrorCode CMOS0_Off(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if CMOS0 pulse is enabled.
// if CMOS0 pulse is disabled, sets the Output Logic Level of CMOS0 low.

__declspec (dllexport) ErrorCode Is_CMOS1_Pulse_Enabled(OPCR_HANDLE opcr_handle, Bool* pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse enable in pulse_en, which must be pre-allocated.
__declspec (dllexport) ErrorCode Enable_CMOS1_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Enables pulse of programmed width and delay to be output when Timing is started.
__declspec (dllexport) ErrorCode Disable_CMOS1_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Disables pulse from being output when Timing is started. This makes CMOS1_On and CMOS1_Off functions valid.
__declspec (dllexport) ErrorCode Is_CMOS1_Individual_Pulse_Enabled(OPCR_HANDLE opcr_handle, int select, Bool* pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// reads the individual pulse enable for pulse 0, 1, 2, or 3, as indicated by select, and writes to pulse_en, which must be pre-allocated.
__declspec (dllexport) ErrorCode CMOS1_Individual_Pulse_Enable(OPCR_HANDLE opcr_handle, int select, Bool pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// writes the individual pulse enable for pulse 0, 1, 2, or 3, as indicated by select, according to pulse_en. Set_Timing_CMOS1 function also enables the individual pulse selected.
__declspec (dllexport) ErrorCode Is_CMOS1_Pulse_Inverted(OPCR_HANDLE opcr_handle, Bool* inverted);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse invert in inverted, which must be pre-allocated.
__declspec (dllexport) ErrorCode CMOS1_Pulse_Invert(OPCR_HANDLE opcr_handle, Bool invert);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// sets the state of the pulse invert according to invert.
__declspec (dllexport) ErrorCode Get_Timing_CMOS1(OPCR_HANDLE opcr_handle, int select, double* cmos1_width, double* cmos1_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// cmos1_width and cmos1_delay must be pre-allocated.
// Set_Timing_CMOS1 function below for more details.
__declspec (dllexport) ErrorCode Set_Timing_CMOS1(OPCR_HANDLE opcr_handle, int pulse_period, int select, double cmos1_width, double cmos1_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Use this function to setup the four available CMOS1 pulses if not used as rcvr shutter pulses.
// writes the pulse width and delay for pulse 0, 1, 2, or 3, as indicated by select, according to pulse_en.
// cmos1_width range is 2 to (pulse_period-2) and must be a multiple of 0.5, i.e. 2.0, 2.5, 3.0, 3.5, etc.
// cmos1_delay range is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5.
// also enables the individual pulse selected.
// pulse_period is only read by this function; use Set_Timing_Basic or Set_Timing_CRI4200 to set pulse_period..
__declspec (dllexport) ErrorCode Is_CMOS1_On(OPCR_HANDLE opcr_handle, Bool* logic_level);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the Output Logic Level CMOS1 in logic_level, which must be pre-allocated.
__declspec (dllexport) ErrorCode CMOS1_On(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if CMOS1 pulse is enabled.
// if CMOS1 pulse is disabled, sets the Output Logic Level of CMOS1 high.
__declspec (dllexport) ErrorCode CMOS1_Off(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if CMOS1 pulse is enabled.
// if CMOS1 pulse is disabled, sets the Output Logic Level of CMOS1 low.

__declspec (dllexport) ErrorCode Is_CMOS2_Pulse_Enabled(OPCR_HANDLE opcr_handle, Bool* pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse enable in pulse_en, which must be pre-allocated.
__declspec (dllexport) ErrorCode Enable_CMOS2_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Enables pulse of programmed width and delay to be output when Timing is started.
__declspec (dllexport) ErrorCode Disable_CMOS2_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Disables pulse from being output when Timing is started. This makes CMOS2_On and CMOS2_Off functions valid.
__declspec (dllexport) ErrorCode Is_CMOS2_Pulse_Inverted(OPCR_HANDLE opcr_handle, Bool* inverted);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse invert in inverted, which must be pre-allocated.
__declspec (dllexport) ErrorCode CMOS2_Pulse_Invert(OPCR_HANDLE opcr_handle, Bool invert);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// sets the state of the pulse invert according to invert.
__declspec (dllexport) ErrorCode Get_Timing_CMOS2(OPCR_HANDLE opcr_handle, double* cmos2_width, double* cmos2_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// cmos2_width and cmos2_delay must be pre-allocated.
// Set_Timing_CMOS2 function below for more details.
__declspec (dllexport) ErrorCode Set_Timing_CMOS2(OPCR_HANDLE opcr_handle, int pulse_period, double cmos2_width, double cmos2_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Use this function to setup the CMOS2 pulse if not used as delay coil select.
// cmos2__width range is 2 to (pulse_period-2) and must be a multiple of 0.5, i.e. 2.0, 2.5, 3.0, 3.5, etc.
// cmos2__delay range is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5.
// pulse_period is only read by this function; use Set_Timing_Basic or Set_Timing_CRI4200 to set pulse_period.
__declspec (dllexport) ErrorCode Is_CMOS2_On(OPCR_HANDLE opcr_handle, Bool* logic_level);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the Output Logic Level CMOS2 in logic_level, which must be pre-allocated.
__declspec (dllexport) ErrorCode CMOS2_On(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if CMOS2 pulse is enabled.
// if CMOS2 pulse is disabled, sets the Output Logic Level of CMOS2 high.
__declspec (dllexport) ErrorCode CMOS2_Off(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if CMOS2 pulse is enabled.
// if CMOS2 pulse is disabled, sets the Output Logic Level of CMOS2 low.

__declspec (dllexport) ErrorCode Is_CMOS3_Pulse_Enabled(OPCR_HANDLE opcr_handle, Bool* pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse enable in pulse_en, which must be pre-allocated.
__declspec (dllexport) ErrorCode Enable_CMOS3_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Enables pulse of programmed width and delay to be output when Timing is started.
__declspec (dllexport) ErrorCode Disable_CMOS3_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Disables pulse from being output when Timing is started. This makes CMOS3_On and CMOS3_Off functions valid.
__declspec (dllexport) ErrorCode Is_CMOS3_Pulse_Inverted(OPCR_HANDLE opcr_handle, Bool* inverted);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse invert in inverted, which must be pre-allocated.
__declspec (dllexport) ErrorCode CMOS3_Pulse_Invert(OPCR_HANDLE opcr_handle, Bool invert);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// sets the state of the pulse invert according to invert.
__declspec (dllexport) ErrorCode Get_Timing_CMOS3(OPCR_HANDLE opcr_handle, double* cmos3_width, double* cmos3_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// cmos3_width and cmos3_delay must be pre-allocated.
// Set_Timing_CMOS3 function below for more details.
__declspec (dllexport) ErrorCode Set_Timing_CMOS3(OPCR_HANDLE opcr_handle, int pulse_period, double cmos3_width, double cmos3_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Use this function to setup the CMOS3 pulse if not used as delay coil select.
// cmos3__width range is 2 to (pulse_period-2) and must be a multiple of 0.5, i.e. 2.0, 2.5, 3.0, 3.5, etc.
// cmos3__delay range is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5.
// pulse_period is only read by this function; use Set_Timing_Basic or Set_Timing_CRI4200 to set pulse_period.
__declspec (dllexport) ErrorCode Is_CMOS3_On(OPCR_HANDLE opcr_handle, Bool* logic_level);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the Output Logic Level CMOS3 in logic_level, which must be pre-allocated.
__declspec (dllexport) ErrorCode CMOS3_On(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if CMOS3 pulse is enabled.
// if CMOS3 pulse is disabled, sets the Output Logic Level of CMOS3 high.
__declspec (dllexport) ErrorCode CMOS3_Off(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if CMOS3 pulse is enabled.
// if CMOS3 pulse is disabled, sets the Output Logic Level of CMOS3 low.

__declspec (dllexport) ErrorCode Is_LVDS1_Pulse_Enabled(OPCR_HANDLE opcr_handle, Bool* pulse_en);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse enable in pulse_en, which must be pre-allocated.
__declspec (dllexport) ErrorCode Enable_LVDS1_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Enables pulse of programmed width and delay to be output when Timing is started.
__declspec (dllexport) ErrorCode Disable_LVDS1_Pulse(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Disables pulse from being output when Timing is started. This makes LVDS1_On and LVDS1_Off functions valid.
__declspec (dllexport) ErrorCode Is_LVDS1_Pulse_Inverted(OPCR_HANDLE opcr_handle, Bool* inverted);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the state of the pulse invert in inverted, which must be pre-allocated.
__declspec (dllexport) ErrorCode LVDS1_Pulse_Invert(OPCR_HANDLE opcr_handle, Bool invert);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// sets the state of the pulse invert according to invert.
__declspec (dllexport) ErrorCode Get_Timing_LVDS1(OPCR_HANDLE opcr_handle, double* lvds1_width, double* lvds1_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// lvds1_width and lvds1_delay must be pre-allocated.
// Set_Timing_LVDS1 function below for more details.
__declspec (dllexport) ErrorCode Set_Timing_LVDS1(OPCR_HANDLE opcr_handle, int pulse_period, double lvds1_width, double lvds1_delay);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// Use this function to setup the LVDS1 pulse, which has no dedicated or optional use currently.
// lvds1__width range is 2 to (pulse_period-2) and must be a multiple of 0.5, i.e. 2.0, 2.5, 3.0, 3.5, etc.
// lvds1__delay range is -(pulse_period-0.5) to +(pulse_period-0.5) and must be a multiple of 0.5.
// pulse_period is only read by this function; use Set_Timing_Basic or Set_Timing_CRI4200 to set pulse_period.
__declspec (dllexport) ErrorCode Is_LVDS1_On(OPCR_HANDLE opcr_handle, Bool* logic_level);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns the Output Logic Level LVDS1 in logic_level, which must be pre-allocated.
__declspec (dllexport) ErrorCode LVDS1_On(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if LVDS1 pulse is enabled.
// if LVDS1 pulse is disabled, sets the Output Logic Level of LVDS1 high.
__declspec (dllexport) ErrorCode LVDS1_Off(OPCR_HANDLE opcr_handle);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200 or CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if LVDS1 pulse is enabled.
// if LVDS1 pulse is disabled, sets the Output Logic Level of LVDS1 low.

__declspec (dllexport) ErrorCode Is_AUX_OUT_Timing_Enabled(OPCR_HANDLE opcr_handle, Bool* timing_en);
// This function is optional on CRI-4200 and CRI-4400 interrogator instruments.
// This returns the state of AUX_OUT (ttl3) clock enable in timing_en, which must be pre-allocated.
// If Config is Internal Clock, External 10MHz Clock, or External 25MHz Clock, then AUX OUT is Manual Control (default) or 25MHz Clock.
// If Config is External 100MHz Clock, then AUX OUT is Manual Control (default) or 100MHz Clock.
// If Config is any of the 25MHz or 100MHz deskewed configurations, then AUX OUT is a dedidicated 25MHz or 100MHz Clock supplying AUX IN, and timing_en always = 1.
__declspec (dllexport) ErrorCode Enable_AUX_OUT_Timing(OPCR_HANDLE opcr_handle);
// This function is optional on CRI-4200 and CRI-4400 interrogator instruments.
// For non-deskewed configurations, enables AUX_OUT (ttl3) 25MHz or 100MHz clock out.
// For deskewed configurations, returns opcr_invalid_function error if ttl3 clock is enabled since AUX_OUT (ttl3) is a dedicative 25MHz or 100MHz clock for deskewing and timing_en always = 1.
__declspec (dllexport) ErrorCode Disable_AUX_OUT_Timing(OPCR_HANDLE opcr_handle);
// This function is optional on CRI-4200 and CRI-4400 interrogator instruments.
// For non-deskewed configurations, disables AUX_OUT (ttl3) 25MHz or 100MHz clock out.
// For deskewed configurations, returns opcr_invalid_function error if ttl3 clock is enabled since AUX_OUT (ttl3) is a dedicative 25MHz or 100MHz clock for deskewing and timing_en always = 1.
__declspec (dllexport) ErrorCode Is_AUX_OUT_On(OPCR_HANDLE opcr_handle, Bool* logic_level);
// This function is optional on CRI-4200 and CRI-4400 interrogator instruments.
// returns the Output Logic Level AUX_OUT (ttl3) in logic_level, which must be pre-allocated.
__declspec (dllexport) ErrorCode AUX_OUT_On(OPCR_HANDLE opcr_handle);
// This function is optional on CRI-4200 and CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if AUX_OUT (ttl3) clock is enabled.
// if AUX_OUT (ttl3) clock timing is disabled, sets the Output Logic Level of ttl3 high.
__declspec (dllexport) ErrorCode AUX_OUT_Off(OPCR_HANDLE opcr_handle);
// This function is optional on CRI-4200 and CRI-4400 interrogator instruments.
// returns opcr_invalid_function error if ttl3 clock is enabled.
// if AUX_OUT (ttl3) clock timing is disabled, sets the Output Logic Level of ttl3 low.

__declspec (dllexport) ErrorCode Get_Optical_Delay_Coil(OPCR_HANDLE opcr_handle, coil_delay* delay_select);
// This function is not appicable for instruments whose InstrumentOptions.compensator_type is 1, 2, 3,or 7 (fixed delay), like the CRI-3200, CRI-2200P1, CRI-4200P1, or CRI-4200 interrogator instruments, but
// when not appicable, it essential returns a value corresponding to CMOS2 and CMOS3 logic state.
// This function is valid for instruments whose InstrumentOptions.compensator_type is 4, 5, or 6 (multiple delay), like the CRI-4400 interrogator instrument.
// This function gets the delay coils selection from one of four compensator delay coils used for setting interrogator spatial resolution, and writes to delay_select which must be pre-allocated.
// The length of the of the four delays coils are identified by InstrumentOptions.compensator_type read from the Get_Instrument_Info function.
__declspec (dllexport) ErrorCode Set_Optical_Delay_Coil(OPCR_HANDLE opcr_handle, coil_delay delay_select);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.compensator_type is 1, 2, 3, or 7 (fixed delay), like the CRI-3200, CRI-2200P1, CRI-4200P1, or CRI-4200 interrogator instruments.
// This function is valid for instruments whose InstrumentOptions.compensator_type is 4, 5, 6, or 8 through 15 (multiple delay), like the CRI-4400 interrogator instrument.
// This function selects one of four compensator delay coils used for setting interrogator spatial resolution.
// The length of the of the four delays coils are identified by InstrumentOptions.compensator_type read from the Get_Instrument_Info function.
// delay_select must be 0, 1, 2, or 3.

__declspec (dllexport) ErrorCode Get_Optical_Rcvr_Amp_Current(OPCR_HANDLE opcr_handle, int* mA);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 1 (fixed current).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 1 (fixed current).
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Gets the Optical Rcvr Amp (EDFA) current in mA.	
// mA range is 0 to 200 mA and must be pre-allocated.
__declspec (dllexport) ErrorCode Set_Optical_Rcvr_Amp_Current(OPCR_HANDLE opcr_handle, int mA);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 1 (fixed current).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 1 (fixed current).
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Sets the Optical Rcvr Amp (EDFA) current, regardless of wether EDFA is on or off.
// The EDFA still requires Optical_Rcvr_Amp_On function to turn on.	
// mA range is 0 to 200 mA.
// As EDFAs age, they may not be capable of acheiving max current or something close to it. If this is the case, the function will return an opcr_optical_amp_command_failed error.
__declspec (dllexport) ErrorCode Set_Optical_Rcvr_Amp_Power_On_Current(OPCR_HANDLE opcr_handle, int mA, int flash_timeout_sec);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 1 (fixed current).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 1 (fixed current).
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Sets the Optical Rcvr Amp (EDFA) power on current by setting this value in EDFA's non-volatile flash memory.
// The EDFA still requires Optical_Rcvr_Amp_On function to turn on after power on.
// This function also sets the currently used operating current, in addition to the power on current saved in EDFA flash memory.
// mA range is 0 to 200 mA.
// As EDFAs age, they may not be capable of acheiving max current or something close to it. If this is the case, the function will return an opcr_optical_amp_command_failed error.
// flash_timeout_sec range is 15 to 60 seconds.  The flash write takes a minimum of 15 seconds.
__declspec (dllexport) ErrorCode Get_Optical_Rcvr_Amp_Status(OPCR_HANDLE opcr_handle, Bool* is_on, Bool* is_acc, double* case_temperature);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 1 (fixed current).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 1 (fixed current)..
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// is_on indicates if Optical_Rcvr_Amp is on (TRUE) or is off (FALSE) and must be pre-allocated.
// is_acc indicates if Optical_Rcvr_Amp mode is ACC (TRUE) or is not ACC (FALSE) and must be pre-allocated. Optical_Rcvr_Amp mode should always be ACC.
// case_temperature is the EDFA case_temperature in degrees Celsius and must be pre-allocated.
	// If Rcvr EDFA is experiencing a High Case Temperature Alarm at 61C or higher, the EDFA indicates "CTA" instead of a temperature; in this case the API writes +99.0 to case_temperature.
	// If Case Temperature rises to 63C, the EDFA pump shuts off (EDFA current to zero).
	// If Rcvr EDFA is experiencing a Low Case Temperature Alarm at -1C or lower, the EDFA indicates "LOW" instead of a temperature; in this case the API writes -99.0 to case_temperature.
	// If Case Temperature falls to -3C, the EDFA pump shuts off (EDFA current to zero).
__declspec (dllexport) ErrorCode Get_Optical_Rcvr_Amp_Status2(OPCR_HANDLE opcr_handle, Bool* is_on, Bool* is_acc, int* current, double* case_temperature, double* tec_temperature);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 1 (fixed current / Preamp EDFA).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 1 (fixed current)..
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// is_on indicates if Optical_Rcvr_Amp / Preamp EDFA is on (TRUE) or is off (FALSE) and must be pre-allocated.
// is_acc indicates if Optical_Rcvr_Amp / Preamp EDFA mode is ACC (TRUE) or is not ACC (FALSE) and must be pre-allocated. Optical_Rcvr_Amp / Preamp EDFA mode should always be ACC.
// current is the Optical_Rcvr_Amp / Preamp EDFA current read (versus commanded)
	// When Preamp EDFA is on, this current sometimes varies from commanded current by one or a few mA.
	// When Preamp EDFA is on and experiencing a High Current Alarm, the Preamp EDFA indicates "LDCA" instead of a current; in this case the API writes -1 to current.
	// When Preamp EDFA is off, the Preamp EDFA indicates "LOW" instead of a current; in this case the API writes -2 to current.
// case_temperature is the EDFA case_temperature in degrees Celsius and must be pre-allocated.
	// If Rcvr EDFA is experiencing a High Case Temperature Alarm at 61C or higher, the EDFA indicates "CTA" instead of a temperature; in this case the API writes +99.0 to case_temperature.
	// If Case Temperature rises to 63C, the EDFA pump shuts off (EDFA current to zero).
	// If Rcvr EDFA is experiencing a Low Case Temperature Alarm at -1C or lower, the EDFA indicates "LOW" instead of a temperature; in this case the API writes -99.0 to case_temperature.
	// If Case Temperature falls to -3C, the EDFA pump shuts off (EDFA current to zero).
// tec_temperature is the EDFA Pump temperature, being maintained by the TEC, in degrees Celsius and must be pre-allocated.
	// tec_temperature should read 25.0 C when operating properly.
	// If EDFA is experiencing a Pump Temperature Alarm at 27.1C or higher, the EDFA indicates "PTA" instead of a temperature; in this case the API writes +99.0 to tec_temperature.
	// If Pump Temperature rises to 30C, the EDFA pump shuts off (EDFA current to zero).
__declspec (dllexport) ErrorCode Optical_Rcvr_Amp_On(OPCR_HANDLE opcr_handle);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 1 (fixed current).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 1 (fixed current).
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Turns the Optical Rcvr Amp (EDFA) on.  The current(mA) value the EDFA uses when turned on is whatever the last current(mA) that was commanded to the EDFA using Set_Optical_Rcvr_Amp_Current,
// or its "power on" current setting loaded into the EDFAs flash memory. 
__declspec (dllexport) ErrorCode Optical_Rcvr_Amp_Off(OPCR_HANDLE opcr_handle);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 1 (fixed current).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 1 (fixed current).
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Turns the Optical Rcvr Amp (EDFA) off. 
__declspec (dllexport) ErrorCode Write_To_Optical_Rcvr_Amp(OPCR_HANDLE opcr_handle, const char* string_in, char* string_out);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 1 (fixed current).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 1 (fixed current).
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// If more Optical Rcvr EDFA communication, than what is provided by the above six functions, is desired/needed, this function writes a command to the Optical Rcvr EDFA and reads back its response.
// string_in can be up to 32 characters (33 including null terminator).
// proper RS232 terminating character (line feed) is appended to string_in within the function.  
// string_out is the response from the EDFA and must be pre-allocated to contain up to 1024 characters plus the null terminator since 1024 is the size of the WTG Controller's RS232 receive buffer.
// Refer to Nuphoton Technologies NP2000-MSA series Erbium Doped Fiber Amplifier Operating Instructions and User Manual for a list of EDFA commands.

__declspec (dllexport) ErrorCode Get_Ramped_Optical_Rcvr_Amp_Current(OPCR_HANDLE opcr_handle, int* mA);
// mA must be preallocated.
// mA range: 0mA to 350mA.
__declspec (dllexport) ErrorCode Set_Ramped_Optical_Rcvr_Amp_Current(OPCR_HANDLE opcr_handle, int mA);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 2 (ramped current).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 2 (ramped current).
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// For ramped optical rcvr, this function set its current to a fixed value determined by mA.
// mA range: 0mA to 350mA.
// Calling this function disables ramp, which means ramp will NOT be on when Timing is On (Pulse & Acquisition Trigger).
__declspec (dllexport) ErrorCode Get_Ramped_Optical_Rcvr_Amp_Ramp(OPCR_HANDLE opcr_handle, int* initial_mA, int* ramp_delay, double* ramp_rate_mA_per_clock_cycle, Bool* is_enabled);
// initial_mA, ramp_delay, ramp_rate_mA_per_clock_cycle, and is_enabled must be preallocated.
// initial_mA range is 0 to 350mA and will be applied from the start of pulse_period until ramp_delay clock cycles, then the current will begin to ramp, and continue to ramp until
// 256 clock cycles before the end of pulse_period, where it will return to initial_mA to allow the rcvr current to settle to initial_mA before the beginning of the next pulse_period.
// ramp_delay is in units of "System Clock Cycles" (typically 10ns) and its range is 0 to (pulse_period - 257).
// ramp_rate_mA_per_clock_cycle range: 0 to 0.01, which corresponds to about 0 to 10mA per km.
// is_enabled = True means when Timing is On (Pulse & Acquisition Trigger) the ramp is on; otherwise gain current is set to static value by function Set_Ramped_Optical_Rcvr_Amp_Current.
__declspec (dllexport) ErrorCode Set_Ramped_Optical_Rcvr_Amp_Ramp(OPCR_HANDLE opcr_handle, int initial_mA, int ramp_delay, double ramp_rate_mA_per_clock_cycle, int pulse_period);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.optical_rcvr_amp_option is not equal 2 (ramped current).
// This function is valid if InstrumentOptions.optical_rcvr_amp_option = 2 (ramped current).
// Typically optical_rcvr_amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// initial_mA range is 0 to 350mA and will be applied from the start of pulse_period until ramp_delay clock cycles, then the current will begin to ramp, and continue to ramp until
// 256 clock cycles before the end of pulse_period, where it will return to initial_mA to allow the rcvr current to settle to initial_mA before the beginning of the next pulse_period.
// ramp_delay is in units of "System Clock Cycles" (typically 10ns) and its range is 0 to (pulse_period - 257).
// ramp_rate_mA_per_clock_cycle range: 0 to 0.01, which corresponds to about 0 to 10mA per km.
// This function also requires the same pulse_period value used in the Set_Timing function.
// pulse_period is in units of "System Clock Cycles" (typically 10ns) and its range is 500 to 65536.
// Calling this function enables ramp, which means ramp will be on when Timing is On (Pulse & Acquisition Trigger).
// When ramp is enabled and Timing is stopped, Optical Rcvr Current goes to intial_mA.

__declspec (dllexport) ErrorCode Get_Optical_Rcvr_Dither(OPCR_HANDLE opcr_handle, Bool* is_enabled, double* dither_amplitude, int* update_divider);
// Gets dither enabled state, amplitude, and frequency divider.
// is_enabled is TRUE if dither is enabled, which means dither will on when Timing is on. is_enabled must be pre-allocated.
// dither_amplitude is peak-to-peak dither ampitdue in volts, and must be pre-allocated.
// dither frequency (for 100MHz System Clock) = 100MHz / (1000 * update_divider). update_divider must be pre-allocated.
// For example, an update divider of 1,000,000 is for 0.1Hz dither; 100,000 is for 1Hz dither; and 10,000 is for 10Hz dither
__declspec (dllexport) ErrorCode Enable_Optical_Rcvr_Dither(OPCR_HANDLE opcr_handle, double dither_amplitude, int update_divider);
// When Timing is On and Dither is enabled, dither will be on and to the desired dither amplitude and frequency.
// dither_amplitude range is 0V to 4V, recommended dither_amplitude is 1.2V.
// update_divider range is 10,000 to 1,000,000
// The dither is a 1000 point sinusoid with an update rate for each point of System Clock (typically 100MHz) divided by update_divider,
// so dither period = (1000 * update_divider) / 100MHz; and dither frequency = 100MHz / (1000 * update_divider).
// For example, set update divider to 1,000,000 for 0.1Hz dither, 100,000 for 1Hz dither, and 10,000 for 10Hz dither
__declspec (dllexport) ErrorCode Disable_Optical_Rcvr_Dither(OPCR_HANDLE opcr_handle);
// Turns dither off.

__declspec (dllexport) ErrorCode Get_Electronic_Rcvr_Amp_Gain(OPCR_HANDLE opcr_handle, double* dB);
// dB must be preallocated.
// dB range: -10.0dB to +30.0dB.
__declspec (dllexport) ErrorCode Set_Electronic_Rcvr_Amp_Gain(OPCR_HANDLE opcr_handle, double dB);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.electronic_rcvr_amp_option is not equal 1 (fixed current).
// This function is valid if InstrumentOptions.electronic_rcvr_amp_option = 1 (fixed current).
// Typically electronic_rcvr_amp_option = 0 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Sets the Electronic Rcvr to fixed gain according to dB.
// dB range: -10.0dB to +30.0dB.
__declspec (dllexport) ErrorCode Get_Ramped_Electronic_Rcvr_Amp_Gain(OPCR_HANDLE opcr_handle, double* dB);
// dB range: -10.0dB to +30.0dB.
__declspec (dllexport) ErrorCode Set_Ramped_Electronic_Rcvr_Amp_Gain(OPCR_HANDLE opcr_handle, double dB);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.electronic_rcvr_amp_option is not equal 2 (ramped current).
// This function is valid if InstrumentOptions.electronic_rcvr_amp_option = 2 (ramped current).
// Typically electronic_rcvr_amp_option = 0 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Sets the Ramped Electronic Rcvr to fixed gain according to dB.
// dB range: -10.0dB to +30.0dB.
// Calling this function disables ramp, which means ramp will NOT be on when Timing is On (Pulse & Acquisition Trigger).
__declspec (dllexport) ErrorCode Get_Ramped_Electronic_Rcvr_Amp_Ramp(OPCR_HANDLE opcr_handle, double* initial_dB, int* ramp_delay, double* ramp_rate_dB_per_clock_cycle, Bool* is_enabled);
// initial_dB, ramp_delay, ramp_rate_dB_per_clock_cycle, and is_enabled must be preallocated.
// initial_dB range is -10.0dB to +30.0dB and will be applied from the start of pulse_period until ramp_delay clock cycles, then the gain will begin to ramp, and continue to ramp until
// 256 clock cycles before the end of pulse_period, where it will return to initial_dB to allow the rcvr gain to settle to initial_dB before the beginning of the next pulse_period.
// ramp_delay is in units of "System Clock Cycles" (typically 10ns) and its range is 0 to (pulse_period - 257).
// ramp_rate_dB_per_clock_cycle range is 0 to 0.0030, which corresponds to about 0 to 3dB per km.
// is_enabled = True means when Timing is On (Pulse & Acquisition Trigger) the ramp is on; otherwise gain is set to static value by function Set_Ramped_Electronic_Rcvr_Amp_Gain.
__declspec (dllexport) ErrorCode Set_Ramped_Electronic_Rcvr_Amp_Ramp(OPCR_HANDLE opcr_handle, double initial_dB, int ramp_delay, double ramp_rate_dB_per_clock_cycle, int pulse_period);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.electronic_rcvr_amp_option is not equal 2 (ramped current).
// This function is valid if InstrumentOptions.electronic_rcvr_amp_option = 2 (ramped current).
// Typically electronic_rcvr_amp_option = 0 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// initial_dB range is -10.0dB to +30.0dB and will be applied from the start of pulse_period until ramp_delay clock cycles, then the gain will begin to ramp, and continue to ramp until
// 256 clock cycles before the end of pulse_period, where it will return to initial_dB to allow the rcvr gain to settle to initial_dB before the beginning of the next pulse_period.
// ramp_delay is in units of "System Clock Cycles" (typically 10ns) and its range is 0 to (pulse_period - 257).
// ramp_rate_dB_per_clock_cycle range is 0 to 0.003, which corresponds to about 0 to 3dB per km.
// This function also requires the same pulse_period value used in the Set_Timing function.
// pulse_period is in units of "System Clock Cycles" (typically 10ns) and its range is 500 to 65536.
// Calling this function enables ramp, which means ramp will be on when Timing is On (Pulse & Acquisition Trigger).
// When ramp is enabled and Timing is stopped, Electronic Rcvr Gain goes to intial_dB.

__declspec (dllexport) ErrorCode Get_Optical_Output_Amp_Current(OPCR_HANDLE opcr_handle, int* mA);
// This function is applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Gets the Optical Rcvr Amp (EDFA) current in mA.	
// mA range is 0 to 300 mA for optical_out_amp_type = 1.
// mA range is 0 to 1300 mA for optical_out_amp_type = 2.
// mA range must be pre-allocated.
__declspec (dllexport) ErrorCode Set_Optical_Output_Amp_Current(OPCR_HANDLE opcr_handle, int mA);	
// This function is applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Sets the Optical Output Amp (EDFA) current independent of whether the Optical Output Amp (EDFA) is on or off.
// If Optical Output Amp is Off, this is the current the Optical Output Amp (EDFA) will use when it turns on.
// mA range is 0 to 300 mA for optical_out_amp_type = 1.
// mA range is 0 to 1300 mA for optical_out_amp_type = 2.
// As EDFAs age, they may not be capable of achieving max current or close to it. If this is the case, the function will return an opcr_optical_amp_command_failed error.
__declspec (dllexport) ErrorCode Set_Optical_Output_Amp_Power_On_Current(OPCR_HANDLE opcr_handle, int mA, int flash_timeout_sec);
// This function is applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Sets the Optical Output Amp (EDFA) power on current by setting this value in EDFA's non-volatile flash memory.
// The EDFA still requires Optical_Output_Amp_On function to turn on after power on.
// This function also sets the currently used operating current, in addition to the power on current saved in EDFA flash memory.
// mA range is 0 to 300 mA for optical_out_amp_type = 1.
// mA range is 0 to 1300 mA for optical_out_amp_type = 2.
// As EDFAs age, they may not be capable of acheiving max current or something close to it. If this is the case, the function will return an opcr_optical_amp_command_failed error.
// flash_timeout_sec range is 15 to 60 seconds.  The flash write takes a minimum of 15 seconds.
__declspec (dllexport) ErrorCode Get_Optical_Output_Amp_Status(OPCR_HANDLE opcr_handle, Bool* is_on, Bool* is_acc, double* case_temperature);
// This function is applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// is_on indicates if Optical_Output_Amp is on (TRUE) or is off (FALSE) and must be pre-allocated.
// is_acc indicates if Optical_Output_Amp mode is ACC (TRUE) or is not ACC (FALSE) and must be pre-allocated. Optical_Output_Amp mode should always be ACC.
// case_temperature is the EDFA case_temperature in degrees Celsius and must be pre-allocated.
	// If Output EDFA is experiencing a High Case Temperature Alarm at 71C or higher, the EDFA indicates "CTA" instead of a temperature; in this case the API writes +99.0 to case_temperature.
	// If Case Temperature rises to 73C, the EDFA pump shuts off (EDFA current to zero).
	// If Output EDFA is experiencing a Low Case Temperature Alarm at -6C or lower, the EDFA indicates "LOW" instead of a temperature; in this case the API writes -99.0 to case_temperature.
	// If Case Temperature falls to -8C, the EDFA pump shuts off (EDFA current to zero).
__declspec (dllexport) ErrorCode Get_Optical_Output_Amp_Status2(OPCR_HANDLE opcr_handle, Bool* is_on, Bool* is_acc, int* current, double* case_temperature, double* tec_temperature);
// This function returns opcr_invalid_function error for instruments whose InstrumentOptions.Optical_Output_Amp_option is not equal 1 (fixed current / Booster EDFA).
// This function is valid if InstrumentOptions.Optical_Output_Amp_option = 1 (fixed current)..
// Typically Optical_Output_Amp_option = 1 for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// is_on indicates if Optical_Output_Amp / Booster EDFA is on (TRUE) or is off (FALSE) and must be pre-allocated.
// is_acc indicates if Optical_Output_Amp / Booster EDFA mode is ACC (TRUE) or is not ACC (FALSE) and must be pre-allocated. Optical_Output_Amp / Booster EDFA mode should always be ACC.
// current is the Optical_Output_Amp / Booster EDFA current read (versus commanded)
	// When Booster EDFA is on, this current sometimes varies from commanded current by one or a few mA.
	// When Booster EDFA is on and experiencing a High Current Alarm, the Booster EDFA indicates "LDCA" instead of a current; in this case the API writes -1 to current.
	// When Booster EDFA is off, the Booster EDFA does not indicate "LOW" instead of a current (like the Preamp), but instead indicates a very low current value.
	// When Booster EDFA is off, if the Booster EDFA were to indicate "LOW" instead of a current, the API writes -2 to current.
// case_temperature is the EDFA case_temperature in degrees Celsius and must be pre-allocated.
	// If Output EDFA is experiencing a High Case Temperature Alarm at 71C or higher, the EDFA indicates "CTA" instead of a temperature; in this case the API writes +99.0 to case_temperature.
	// If Case Temperature rises to 73C, the EDFA pump shuts off (EDFA current to zero).
	// If Output EDFA is experiencing a Low Case Temperature Alarm at -6C or lower, the EDFA indicates "LOW" instead of a temperature; in this case the API writes -99.0 to case_temperature.
	// If Case Temperature falls to -8C, the EDFA pump shuts off (EDFA current to zero).
// tec_temperature is the EDFA Pump temperature, being maintained by the TEC, in degrees Celsius and must be pre-allocated.
	// tec_temperature should read 25.0 C when operating properly.
	// If EDFA is experiencing a Pump Temperature Alarm at 27.1C or higher, the EDFA indicates "PTA" instead of a temperature; in this case the API writes +99.0 to tec_temperature.
	// If Pump Temperature rises to 30C, the EDFA pump shuts off (EDFA current to zero).
__declspec (dllexport) ErrorCode Optical_Output_Amp_On(OPCR_HANDLE opcr_handle);
// This function is applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Turns the Optical Output Amp (EDFA) on. The current(mA) value the EDFA uses when turned on is whatever the last current(mA) that was commanded to the EDFA using Set_Optical_Rcvr_Amp_Current,
// or its "power on" current setting loaded into the EDFAs flash memory.
__declspec (dllexport) ErrorCode Optical_Output_Amp_Off(OPCR_HANDLE opcr_handle);
// This function is applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// Turns the Optical Output Amp (EDFA) off.
__declspec (dllexport) ErrorCode Write_To_Optical_Output_Amp(OPCR_HANDLE opcr_handle, const char* string_in, char* string_out);
// This function is applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, and CRI-4400 interrogator instruments.
// If more Optical Output EDFA communication, than what is provided by the previous six functions, is desired/needed, this function writes a command to the Optical Output EDFA and reads back its response.
// string_in can be up to 32 characters (33 including null terminator).
// proper RS232 terminating character (line feed) is appended to string_in within the function.  
// string_out is the response from the EDFA and must be pre-allocated to contain up to 1024 characters plus the null terminator since 1024 is the size of the WTG Controller's RS232 receive buffer.
// Refer to Nuphoton Technologies NP2000-MSA series Erbium Doped Fiber Amplifier Operating Instructions and User Manual for a list of EDFA commands.

__declspec (dllexport) ErrorCode Get_Laser_Firmware_Version(OPCR_HANDLE opcr_handle, int laser_number, int* major_version, int* minor_version, int* patch);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Gets the Laser Firmware major_version, minor_version, and patch.	
// major_version, minor_version, and patch must be pre-allocated.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Get_Laser_ITU(OPCR_HANDLE opcr_handle, int laser_number, int* itu);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Gets the integer corresponding to the Laser ITU band.	
// itu must be pre-allocated.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Get_Laser_Current(OPCR_HANDLE opcr_handle, int laser_number, double* mA);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Gets the Laser current in milliamps.	
// mA range is 0 to 200mA and it must be pre-allocated.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Set_Laser_Current(OPCR_HANDLE opcr_handle, int laser_number, double mA);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Sets the Laser current in milliamps.	
// mA range is 0 to 200mA.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Get_Laser_Power_On_Current(OPCR_HANDLE opcr_handle, int laser_number, double* mA);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Gets the power on Laser current (via Laser flash memory) in milliamps.	
// mA range is 0 to 200mA and it must be pre-allocated.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Set_Laser_Power_On_Current(OPCR_HANDLE opcr_handle, int laser_number, double mA);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Sets the power on Laser current (via Laser flash memory) in milliamps.	
// mA range is 0 to 200mA.
// Also sets the currently used operating current, in addition to the power on current saved in Laser flash memory.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Get_Laser_TEC_Setpoint(OPCR_HANDLE opcr_handle, int laser_number, int* ohms);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Gets the Laser TEC thermistor set-point in ohms.	
// ohms range is 0 to 65535 and must be pre-allocated.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Set_Laser_TEC_Setpoint(OPCR_HANDLE opcr_handle, int laser_number, int ohms);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Sets the Laser TEC thermistor set-point in ohms.	
// ohms range is 0 to 65535.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Get_Laser_Power_On_TEC_Setpoint(OPCR_HANDLE opcr_handle, int laser_number, int* ohms);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Gets the power on Laser TEC thermistor set-point (via Laser flash memory) in ohms.	
// ohms range is 0 to 65535 and must be pre-allocated.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Set_Laser_Power_On_TEC_Setpoint(OPCR_HANDLE opcr_handle, int laser_number, int ohms);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Sets the power on Laser TEC thermistor set-point (via Laser flash memory) in ohms.
// ohms range is 0 to 65535.
// Also sets the currently used TEC thermistor set-point, in addition to the power-on TEC thermistor set-point saved in EDFA flash memory.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Get_Laser_TEC_Actual(OPCR_HANDLE opcr_handle, int laser_number, int* ohms);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Gets the power on Laser TEC thermistor set-point (via Laser flash memory) in ohms.	
// ohms range is to 262,080,000 and must be pre-allocated.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Get_Laser_PD_Monitor(OPCR_HANDLE opcr_handle, int laser_number, double* mA);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Gets the Laser photo diode monitor current in milliamps.	
// mA range is 0 to 2.5 mA and it must be pre-allocated.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Get_Laser_PCB_Temp(OPCR_HANDLE opcr_handle, int laser_number, double* celsius);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.s.
// Gets the Laser PCB temperature in degrees celsius and it must be pre-allocated.	
// celsius possible range is -36.4C to 120.4C but Redfern Integrated Optics (RIO) ORION Laser Module Remote Command Interface shows table from -20C to +90C, which may be its reliable temperature sensing range.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Get_Laser_Status(OPCR_HANDLE opcr_handle, int laser_number, uint16_t* word0, uint16_t* word1, uint16_t* word2);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Gets the Laser Firmware Status word0, word1, and word2. See Redfern Integrated Optics (RIO) ORION Laser Module Remote Command Interface document for description of status words.
// word0, word1, and word2 must be pre-allocated.
// laser_number must be 1 for CRI-4200 and must be 1 or 2 for CRI-4400.
__declspec (dllexport) ErrorCode Write_To_Optical_Output_Laser(OPCR_HANDLE opcr_handle, int laser_number, uint8_t* data_in_array, int length_in, uint8_t* data_out_array, int* length_out);
// This function is not applicable for the CRI-3200, CRI-2200P1, and CRI-4200P1 interrogator instruments or for instruments without Laser RS232 connected to WTG Controller.
// This function is applicable for the CRI-4200 and CRI-4400 interrogator instruments, or for instruments with Laser RS232 connected to WTG Controller.
// If Laser communication is not connected, an opcr_optical_laser_communication_error is returned by the function.
// Writes a command to the Optical Output Laser and reads back its response.
// laser_number must be 1 for a single laser interrogator like CRI-4200 and must be 1 or 2 for a dual laser interrogator like CRI-4400.
// Laser commands and responses are binary, not string.
// Laser commands are either 9 or 11 bytes, so data_in_array must be an array of 9 or 11 bytes/elements and length_in must be 9 or 11.
// Depending on the Laser's response, which is based on the command, 11, 13, 15, 17, or 29 bytes/elements are written to data_out_array, and the corresponding number of bytes/elements is indicated by length_out.
// data_out_array and length_out must be pre-allocated. To accommodate all possible Laser responses, data_out_array should be a pre-allocated array of 29 bytes/elements.
// Refer to Redfern Integrated Optics (RIO) ORION Laser Module Remote Command Interface document for a list of Laser commands and responses and their data structure.
// As recommended by the RIO manual, to reduce noise, the RS232 transmitter should be turned off after communicating with Laser, and therefore turned on prior to communicating with Laser.
// It is up to the user of this function to turn the Laser's RS232 transmitter on and off as recommended.  When powered on, the Laser's RS232 transmitter will be off.

__declspec (dllexport) ErrorCode Get_DAC_A_Voltage(OPCR_HANDLE opcr_handle, double* volts);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// Gets DAC A DC(constant) Voltage and writes to volts, which must be pre-allocated.
// Voltage range is 0.0 to +4.0 Volts.
// For instruments with electronic_rcvr_amp_option = 1, DAC A is used for setting the Electronic Rcvr Gain, so the Set_Electronic_Rcvr_Amp_Gain function should be used instead of this function.
__declspec (dllexport) ErrorCode Set_DAC_A_Voltage(OPCR_HANDLE opcr_handle, double volts);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// Sets DAC A to a DC(constant) Voltage.
// Voltage range is 0.0 to +4.0 Volts.
// For instruments with electronic_rcvr_amp_option = 1, DAC A is used for setting the Electronic Rcvr Gain, so the Set_Electronic_Rcvr_Amp_Gain function should be used instead of this function.
__declspec (dllexport) ErrorCode Get_DAC_B_Voltage(OPCR_HANDLE opcr_handle, double* volts);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// Gets DAC B DC(constant) Voltage and writes to volts, which must be pre-allocated.
// Voltage range is 0.0 to +4.0 Volts.
// For instruments that have dither available, DAC B is used for Dither, so Optical_Rcvr_Dither_On and Optical_Rcvr_Dither_Off functions should be used instead of this function.
__declspec (dllexport) ErrorCode Set_DAC_B_Voltage(OPCR_HANDLE opcr_handle, double volts);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// Sets the DAC B to a DC(constant) Voltage.
// Voltage range is 0.0 to +4.0 Volts.
// For instruments that have dither available, DAC B is used for Dither, so Optical_Rcvr_Dither_On and Optical_Rcvr_Dither_Off functions should be used instead of this function.
__declspec (dllexport) ErrorCode Get_DAC_C_Voltage(OPCR_HANDLE opcr_handle, double* volts);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// Gets DAC C DC(constant) Voltage and writes to volts, which must be pre-allocated.
// Voltage range is 0.0 to +4.0 Volts.
// Voltage range is 0.0 to +2.5 Volts. (for WTG Controller Gen1 only)
// For instruments with modulation ramping, DAC C is used for controlling the Modulation Ramp Rate. Use this function for controlling the Modulation Ramp Rate.
__declspec (dllexport) ErrorCode Set_DAC_C_Voltage(OPCR_HANDLE opcr_handle, double volts);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// Sets the DAC C to a DC(constant) Voltage.
// Voltage range is 0.0 to +4.0 Volts.
// Voltage range is 0.0 to +2.5 Volts. (for WTG Controller Gen1 only)
// For instruments with modulation ramping, DAC C is used for controlling the Modulation Ramp Rate. Use this function for controlling the Modulation Ramp Rate.
__declspec (dllexport) ErrorCode Get_DAC_D_Voltage(OPCR_HANDLE opcr_handle, double* volts);
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// DAC D is not available on instruments that use WTG Controller Gen1, but is available on WTG Controller Gen2 and beyond. 
// Gets DAC D DC(constant) Voltage and writes to volts, which must be pre-allocated.
// Voltage range is -4.0 to +4.0 Volts.
__declspec (dllexport) ErrorCode Set_DAC_D_Voltage(OPCR_HANDLE opcr_handle, double volts);
// returns opcr_invalid_function error if WTG Controller Generation equals 1.
// DAC D is not available on instruments that use WTG Controller Gen1, but is available on WTG Controller Gen2 and later.
// This function is not applicable for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// Sets the DAC D to a DC(constant) Voltage.
// Voltage range is -4.0 to +4.0 Volts.

__declspec (dllexport) ErrorCode Set_Modulator_Ramp(OPCR_HANDLE opcr_handle, int mode, int ramp_width, double ramp_rate_ctrl_voltage, double ramp_delay, int pulse_period);
// This function returns opcr_invalid_function error if model is not CRI-X, making it not valid for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// The modulation ramp occurs once per pulse cycle according to mode.
// The timing of the ramp within each pulse cycle is determined by ramp_width and ramp_delay.
// ramp_rate_ctrl_voltage determines the ramp rate,
	// for a 40nsec (4 clocks) ramp width, typically a ramp_rate_ctrl_voltage greater than 2V, will cause the ramp to saturate before it has ramped for a full 40nsec.
	// for a 60nsec (6 clocks) ramp width, typically a ramp_rate_ctrl_voltage greater than 1.5V, will cause the ramp to saturate before it has ramped for a full 60nsec.
	// for a 80nsec (8 clocks) ramp width, typically a ramp_rate_ctrl_voltage greater than 1.0V, will cause the ramp to saturate before it has ramped for a full 80nsec.
// ramp_rate_ctrl_voltage uses DAC C.
// ramp_rate_ctrl_voltage range is 0 to 2.5V.
// mode = 0 means ramp up, down, up, down, etc.
// mode = 1 menas ramp up, flat, down, up, flat, down, etc.
// ramp_width range is 4 to 2*(pulse_period)/3 - 8, and must be a multiple of 2, i.e. 4, 6, 8, etc.
// ramp_delay range is -(pulse_period-0.5) to (pulse_period-0.5) and must be a multiple of 0.5.
// ramp_width and ramp_delay determine ramp timing for the Optiphase Ramp Driver PCB used to drive an Optical Phase Modulator.
// This function and its parameters are not associated with electronic rcvr or optical rcvr gain/current ramping.
// This function also requires the same pulse_period value used in the Set_Timing function.
// pulse_period is in units of "System Clock Cycles" (typically 10ns) and its range is 500 to 65536.
__declspec (dllexport) ErrorCode Enable_Modulator_Ramp(OPCR_HANDLE opcr_handle);
// This function returns opcr_invalid_function error if model is not CRI-X, making it not valid for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// Enables the Modulation Ramp to be on once Timing is on.
__declspec (dllexport) ErrorCode Disable_Modulator_Ramp(OPCR_HANDLE opcr_handle);
// This function returns opcr_invalid_function error if model is not CRI-X, making it not valid for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments..
// Disables Modulation Ramp from being on once Timing is on, and turns Ramp off whether timing is on or not.

__declspec (dllexport) ErrorCode Set_Polarity_Switching(OPCR_HANDLE opcr_handle, int mode, double volts, int delay, int pulse_period);
// This function returns opcr_invalid_function error if model is not CRI-X, making it not valid for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// This function returns opcr_invalid_function error if either electronic_rcvr_control_option or optical_rcvr_control_option = 2.
// This function is used if High Speed DAC is used for Polarity Switching, versus used for Ramped Electronic Rcvr or Ramped Optical Rcvr, i.e. neither electronic_rcvr_control_option nor optical_rcvr_control_option = 2.
// Sets the mode, amplitude voltage, and timing used to when polarity switching the output of the High Speed DAC.
// Switching, or more precisely, toggling between two voltage levels occurs once per pulse cycle or once every other pulse cycle, depending on mode, which can be 0 or 1.
// delay is in units of "System Clock Cycles" (typically 10ns) and its range is -(pulse_period-1) to (pulse_period-1).
// delay determines when Polarity Switching occurs, relative to the rising edge of the optical pulse (like all other timing), if Polarity Switching is enabled.
// This function also requires the same pulse_period value used in the Set_Timing function.
// pulse_period is in units of "System Clock Cycles" (typically 10ns) and its range is 500 to 65536.
// volts range is -4.0V to +4.0V, and results in toggling between volts and -volts.
__declspec (dllexport) ErrorCode Enable_Polarity_Switching(OPCR_HANDLE opcr_handle);
// This function returns opcr_invalid_function error if model is not CRI-X, making it not valid for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// This function returns opcr_invalid_function error if either electronic_rcvr_control_option or optical_rcvr_control_option = 2.
// This function is used if High Speed DAC is used for Polarity Switching, versus used for Ramped Electronic Rcvr or Ramped Optical Rcvr, i.e. neither electronic_rcvr_control_option nor optical_rcvr_control_option = 2.
// Enables Polarity Switching to be on once Timing is on.
__declspec (dllexport) ErrorCode Disable_Polarity_Switching(OPCR_HANDLE opcr_handle);
// This function returns opcr_invalid_function error if model is not CRI-X, making it not valid for the CRI-3200, CRI-2200P1, CRI-4200P1, CRI-4200, or CRI-4400 interrogator instruments.
// This function returns opcr_invalid_function error if either electronic_rcvr_control_option or optical_rcvr_control_option = 2.
// This function is used if High Speed DAC is used for Polarity Switching, versus used for Ramped Electronic Rcvr or Ramped Optical Rcvr, i.e. neither electronic_rcvr_control_option nor optical_rcvr_control_option = 2.
// Disables Polarity Switching from being on once Timing is on, and turns Polarity Switching off whether timing is on or not.

__declspec (dllexport) ErrorCode Get_Instrument_ID(OPCR_HANDLE opcr_handle, char* id);
// Gets the Instrument ID in its raw character string format.
// The Instrument ID contains the instrument model, serial number, and installed options which impact OCPR API operation.
__declspec (dllexport) ErrorCode Set_Instrument_ID(OPCR_HANDLE opcr_handle, const char* id);
// USE THIS FUNCTION WITH CAUTION; improperly setting the Instrument ID in flash can easily make the instrument inoperable or even lead to instrument damage.
// Sets the Instrument ID in its raw character string format.
// The Instrument ID contains the instrument model, serial number, installed component and control options, and calibration timing, which all impact OCPR API and instrument operation.

__declspec (dllexport) ErrorCode Close_Communication(OPCR_HANDLE opcr_handle);
// Closes handle.
__declspec (dllexport) ErrorCode Close_Communication_and_Instrument_Off(OPCR_HANDLE opcr_handle);
// Closes handle.
// After function is called,
	// Reference clock(s) will be off.
	// Timing will be off.
	// Optical Rcvr Dither will be off, and Optical Rcvr Dither amplitude will be 0V (if applicable).
	// Optical Rcvr Amp will be off (if applicable) 
	// Optical Output Amp will be off.
	// Modulation Ramp will be off (if applicable).
	// Polarity Switching will be off (if applicable).

#endif

