#include <Wire.h>
#include <stdio.h>
#include <math.h>


// Addreses of each temp sensor (3) and accelerometer
const int U1Temp = 0x48; // Temp sensor below accelerometer, middle right of board
const int U3Temp = 0x4F; // Temp sensor at top left of board
const int U4Temp = 0x4D; // Temp sensor at bottom left of board
int accelMeter = 0x1D; // Accelerometer
int tempCutOff = 60; // Max temp limit 
float g_z;
float g_y;

// LinAct and Motor Control
// Lin actuator pins
const int pwmPin = 9;
const int pin1 = 8;
const int pin2 = 7;
const int pin3 = 6;

// Drum motor pin
const int drumPWMpin = 3;

int counter = 0;

String message;

float msDelay = 1500;

int messageInt;

float currentSens = 0.0;

float voltage[100];





void tempSensorConfig(int sensorAddr){
  Wire.beginTransmission(sensorAddr);
  // Select configuration register
  Wire.write(0x01);
  // Set continuous conversion, comparator mode, 12-bit resolution
  Wire.write(0x60);
  // Stop I2C Transmission
  Wire.endTransmission();  
}

float calcTemp(int sensorAddr){
  unsigned int data[2];
  
  // Start I2C Transmission
  Wire.beginTransmission(sensorAddr);
  // Select data register
  Wire.write(0x00);
  // Stop I2C Transmission
  Wire.endTransmission();

  // Request 2 bytes of data
  Wire.requestFrom(sensorAddr, 2);

  // Read 2 bytes of data
  // cTemp msb, cTemp lsb
  if(Wire.available() == 2)
  {
    data[0] = Wire.read();
    data[1] = Wire.read();
  }

  float cTemp = (((data[0] * 256) + (data[1] & 0xF0)) / 16) * 0.0625;
  return cTemp;
}

void setup() 
{
  // Initialise I2C communication as MASTER
  Wire.begin();
  // Initialise Serial communication, set baud rate = 9600
  Serial.begin(9600);

  // ****** Temperature sensor configuration ****** //
  tempSensorConfig(U1Temp);
  tempSensorConfig(U3Temp);
  tempSensorConfig(U4Temp);

  

  // ****** ADXL367Z Config ****** //
  // If address of ADXL happens to be different than defined, use that address
  byte error, address;
  int deviceCount = 0;

  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) { 
      deviceCount++;
      // Check that the given address isn't one of the 3 temp sensors
      if(address != U1Temp && address != U3Temp && address != U4Temp){
         accelMeter = address;
      }
    }
  }
  
  // Configure 0x2D register, the POWER_CTL register by setting 
  int POWER_CTL;
  Wire.beginTransmission(accelMeter);
  Wire.write(0x2D); // Address for register
  Wire.requestFrom(accelMeter, 1);
  if (Wire.available() == 1) {
    POWER_CTL = Wire.read();
  }
  Wire.endTransmission();

  // Logical Rshift twice and Lshift back to clear RHS 7 bits (so basically everything except for reserved bit), then + BIN 10 or DEC 2 for measurement mode as per datasheet
  POWER_CTL = (((unsigned int)POWER_CTL >> 7) << 7) + 2; // "unsigned int" to typecast POWER_CTL, which makes the Rshift to behave as logical rather than arithmetic

  // Write new POWER_CTL value to POWER_CTL register
  Wire.beginTransmission(accelMeter);
  Wire.write(0x2D); // Address for register
  Wire.write(POWER_CTL);
  Wire.endTransmission();

  while(!Serial){} // For motor control setup 

  // Lin act.
  pinMode(pwmPin, OUTPUT);
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  pinMode(pin3, OUTPUT);

  // Drum motor
  pinMode(drumPWMpin, OUTPUT);

  pinMode(A0, INPUT);

  delay(300); 
}

void loop()
{
  
  // Convert temperature data
  float cTempU1 = calcTemp(U1Temp);
  float cTempU3 = calcTemp(U3Temp);
  float cTempU4 = calcTemp(U4Temp);

  // Gather and convert Accelerometer data, must be split into 3 seperate begin/endTrans because requesting more than 1 bit off a single read will trigger high
  unsigned int accelData[3];
  // X axis
  Wire.beginTransmission(accelMeter);
  Wire.write(0x08); // x-axis
  Wire.requestFrom(accelMeter, 1);

  if(Wire.available() == 1){
    accelData[0] = Wire.read();
  }

  Wire.endTransmission();

  // Y axis
  Wire.beginTransmission(accelMeter);
  Wire.write(0x09); // y-axis
  Wire.requestFrom(accelMeter, 1);

  if(Wire.available() == 1){
    accelData[1] = Wire.read();
  }

  // Z axis
  Wire.beginTransmission(accelMeter);
  Wire.write(0x0A); // z-axis
  Wire.requestFrom(accelMeter, 1);

  if(Wire.available() == 1){
    accelData[2] = Wire.read();
  }

  Wire.endTransmission();

  Wire.endTransmission();

  //Convert analog accel data into g's
  // Y-data calcs
  float ydata = float(accelData[1]);
  ydata = ydata - 3;
  if (ydata < 0){
    ydata = 255 + ydata;
  }
  if (ydata >= 0 && ydata <= 127){
    g_y = 1-(ydata/64);
  }
  else{
    g_y = 2* ((ydata - 128)/128) -1;
  }

  // Z-data calcs
  float zdata = float(accelData[2]);
  if (zdata >= 0 && zdata <= 127){
    g_z = 1 - (zdata/64);
  }else{
    g_z = 2 * ((zdata - 128)/128) - 1;
  }

  // Set bounds
  if(g_z > 1){
    g_z = 1;
  }else if (g_z < -1){
    g_z = -1;
  }

  if(g_y > 1){
    g_y = 1;
  }else if (g_y < -1){
    g_y = -1;
  }

  // Output data to serial monitor
  Serial.print(cTempU1);
  Serial.print(", ");
  Serial.print(cTempU3);
  Serial.print(", ");
  Serial.print(cTempU4);
  Serial.print(", ");


  for(int i = 0; i < 3; i++){
    Serial.print(accelData[i]); // ############### Work is needed to interpret raw accel data into angles ####################
    Serial.print(", ");
  }

  //currentSens = ((5 * (float(analogRead(A0)) / 1023)) - 2.5) / 0.05;
  //Serial.print(currentSens);
  
  voltage[counter] = (5 * (float(analogRead(A1))) / 1024);

  float sum = 0.0;
  for(int i = 0; i < 100; i++){
    sum += voltage[i];
  }
  //sum = sum / 1024;

  //currentSens = ((sum / 100) - 2.5) / 0.05;
  Serial.print((sum / 100), 4);
  
  counter = (++counter) % 100;


  // Serial.println();

  // For Motor Control: ##################################################

  if(Serial.available() > 0){
    message = Serial.readStringUntil('\n');
  }else{
    message = "No command sent";
  }

  // Init variables for drum
  messageInt = message.toInt();

  Serial.print("," + String(messageInt));
  Serial.println();

  // Initialize tilt
  // ydata = ydata - 0.01;
  // zdata = zdata - 0.0.1;
  // Serial.println(ydata);
  // Serial.println(zdata);
  float tiltY = acosf(g_y)*180/3.14;
  float tiltZ = acosf(g_z)*180/3.14;

  if (message == "UP"){
    setOut();
    //Serial.println("UP commanded");
  } else if (message == "DOWN"){
    setIn();
    //Serial.println("DOWN commanded");
  }else if(messageInt != 0){
    if(message == "0"){
      msDelay = 500;
    }else{
      msDelay = (messageInt * 2) + 500;
    }
    
  }else if (message == "NONE"){
    digitalWrite(pwmPin, LOW);
 
  }else if (message == "Stop Mode"){
    msDelay = 1500;
  }else if (message == "Sleep Mode"){
    setOut();
    msDelay = 1500;
 }else if (cTempU1 > tempCutOff || cTempU3 > tempCutOff || cTempU4 > tempCutOff){
    msDelay = 1500;
    //Serial.println("Safe Mode");
 }
 else if ( tiltY > 20.0 || tiltZ > 20.0){
    setOut();
    msDelay = 1500;
 }
  //delay(1000); // GET RID OF THIS LATER PLASEEEE
  //Serial.println("Y: " + String(tiltY) + ", Z:" + String(tiltZ));
  //Serial.println("Y G force: " + String(g_y) + ", Z G force: " + String(g_z));
  // Drive drum motor
  digitalWrite(3, HIGH);
  /*
  * 500 - 1490 useconds will turn motor in reverse
  * 1510 - 2500 useconds will turn motor forward
  */
  delayMicroseconds(msDelay);
  digitalWrite(3, LOW);
  //Serial.println(msDelay);

}

void setIn(){
    // Set logic to move the LA Out
  digitalWrite(pwmPin, HIGH);
  digitalWrite(pin1, LOW);
  digitalWrite(pin2, HIGH);
  digitalWrite(pin3, HIGH);
}
void setOut(){
  // Set logic to move LA In
  digitalWrite(pwmPin, HIGH);
  digitalWrite(pin1, HIGH);
  digitalWrite(pin2, LOW);
  digitalWrite(pin3, HIGH);
}
