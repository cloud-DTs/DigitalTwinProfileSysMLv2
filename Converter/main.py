from sysml2py.formatting import classtree
from sysml2py import Package, Item, Model, Attribute, Part, Port
from sysml2py import load_grammar as loads

p1 = Package()._set_name("Rocket")
i1 = Item(definition=True)._set_name("Fuel")
i2 = Item()._set_name("Hydrogen")
p1._set_child(i2)
i2._set_typed_by(i1)
p = classtree(p1._get_definition())

text = """package MicroGridExample{

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
        
    }

    abstract #Entity def Battery:>AbstractEntity{
        #constAttribute :>> maxConsumption{
            :>> value default "5.0";
        }
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
                #constAttribute :>> maxConsumption{
                    :>> value = "10.0";
                }
                #component p13:>>sensor;
            }
            #entity kebaP30:AbstractEntity{
                #constAttribute :>> maxConsumption{
                    :>> value = "22.0";
                }
                #component p14:>>sensor;
            }
        }
       
        #database part TimeSeriesDB{
            attribute :>> libTwinDataBaseTier default LibTwinDataBaseTier::HOT;
            attribute :>> libTwinDataBaseType default LibTwinDataBaseType::TIMESERIES;
        }

        #condition CheckBatteryConsumption{
            attribute :>> operator = ComparisonOperator::GREATER_THAN;
            in attribute :>> leftOperand = MicroGrid.battery.p12.consumptionPort.measurement;
            in attribute :>> rightOperand = MicroGrid.battery.maxConsumption;
            attribute :>> result = true;
            #strategyAction alertAction{
                attribute :>> name = "Alert Action";
                attribute :>> strategyType = StrategyType::LAMBDA;
                attribute :>> description = "Alerts when battery consumption is too high";
                attribute :>> pathToCode = "\\path\\to\\alertFunction";
            }
        }

        #MeasureInterface interface def MQTTBroker {
            attribute :>>type = MeasurementInterfaceType::MQTT;
        }
        #measureInterface interface:MQTTBroker connect source ::> MicroGrid.sieVercharge.p13.consumptionPort 
            to target ::> TimeSeriesDB.dataBaseInPort;
        
        #measureInterface interface:MQTTBroker connect source ::> MicroGrid.kebaP30.p14.consumptionPort 
            to target ::> TimeSeriesDB.dataBaseInPort;

        
    }
}"""

q = Model().load(text)

print(q.dump())