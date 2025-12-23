package MicroGridExample{

    private import MetaModelDigitalTwin::*;

    #Component def PAC_Sensor{
            #measure consumptionPort {
                #measureAttribute consumption {
                    :>> dataType default AttributeDataType::DOUBLE;
                }
            }
         
        }

    abstract #Entity def AbstractEntity {
        #constAttribute maxConsumption{
            :>> value default "23.0";
            :>> dataType default AttributeDataType::DOUBLE;
        }
        #component sensor:PAC_Sensor;
        #component ter:PAC_Sensor;
        
    }

    abstract #Entity def Battery:>AbstractEntity{
        #constAttribute :>> maxConsumption{
            :>> value default "5.0";
        }
        #entity test;
        #component batterySensor:>>sensor;
       
    }


    #Twin def MicroGridDigitalTwin{
         #entity MicroGrid {
            #entity battery:Battery{
                #constAttribute :>> maxConsumption{
                    :>> value = "3.0";
                }
                #component p12:>>batterySensor;
                
            }
            #entity sieVercharge:AbstractEntity{
                
                #component p13:>>sensor;
            }
            #entity kebaP30:AbstractEntity{
                #constAttribute :>> maxConsumption{
                }
                #component p14:>>sensor;
            }
        }
        #DataBase def TestDb{
            :>> libTwinDataBaseTier default LibTwinDataBaseTier::HOT;
        }
       
        #database TimeSeriesDB:TestDb{
            :>> libTwinDataBaseType default LibTwinDataBaseType::TIMESERIES;
        }

        #condition CheckBatteryConsumption{
            attribute :>> operator = ComparisonOperator::GREATER_THAN;
            in attribute :>> leftOperand = MicroGrid.battery.p12.consumptionPort.consumption;
            in attribute :>> rightOperand = MicroGrid.battery.maxConsumption;
            attribute :>> result = true;
            #strategyAction alertAction{
                attribute :>> name = "Alert3 Action";
                attribute :>> strategyType = StrategyType::LAMBDA;
                attribute :>> description = "Alerts when battery consumption is too high";
                attribute :>> pathToCode = "\\path\\to\\alertFunction";
            }
        }

        #MeasureInterface interface def MQTTBroker {
            attribute :>>type = MeasurementInterfaceType::MQTT;
        }
        #measureInterface interface:MQTTBroker connect MicroGrid.sieVercharge.p13.consumptionPort 
            to target ::> TimeSeriesDB.dataBaseInPort;
        
        #measureInterface interface:MQTTBroker connect MicroGrid.kebaP30.p14.consumptionPort 
            to target ::> TimeSeriesDB.dataBaseInPort;

        
    }
}