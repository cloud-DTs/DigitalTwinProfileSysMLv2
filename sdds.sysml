package MetaModelDigitalTwin {

    private import DigitalTwinLibrary::*;
    private import Metaobjects::SemanticMetadata;
    public import DigitalTwinLibrary::AttributeDataType;
    public import DigitalTwinLibrary::MeasurementInterfaceType;
    public import DigitalTwinLibrary::LibTwinDataBaseTier;
    public import DigitalTwinLibrary::LibTwinDataBaseType;
    public import DigitalTwinLibrary::ComparisonOperator;
    public import DigitalTwinLibrary::StrategyType;

    metadata def testr specializes SemanticMetadata{

    }
    metadata def Twin specializes SemanticMetadata {
        redefines baseType = LibTwin meta SysML::PartDefinition;
        subsets annotatedElement : SysML::Definition;
        
    }

    metadata def Entity specializes SemanticMetadata{
        redefines baseType = LibTwinEntity meta SysML::PartDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def entity specializes SemanticMetadata{
        redefines baseType = libTwinEntities meta SysML::PartUsage;
        subsets annotatedElement : SysML::Usage;
    }
    
    metadata def Component specializes SemanticMetadata{
        redefines baseType = LibTwinComponent meta SysML::PartDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def component specializes SemanticMetadata{
        redefines baseType = cmponents meta SysML::PartUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def DataBase specializes SemanticMetadata{
        redefines baseType =LibTwinDataBase meta SysML::PartDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def database specializes SemanticMetadata{
        redefines baseType = dataBases meta SysML::PartUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def MeasureInterface specializes SemanticMetadata{
        redefines baseType=MeasurementInterface meta SysML::InterfaceDefinition;
        subsets annotatedElement : SysML::InterfaceDefinition;
    }

    metadata def measureInterface specializes SemanticMetadata{
        redefines baseType=measurementInterfaces meta SysML::InterfaceUsage;
        subsets annotatedElement : SysML::InterfaceUsage;
    }

    metadata def Measurement specializes SemanticMetadata{
        redefines baseType=MeasurePort meta SysML::PortDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def measure specializes SemanticMetadata{
        redefines baseType=measurements meta SysML::PortUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def ConstAttribute specializes SemanticMetadata{
        redefines baseType=ConstAttributes meta SysML::AttributeDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def MeasureAttribute specializes SemanticMetadata{
        redefines baseType=LibDTAttributes meta SysML::AttributeDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def constAttribute specializes SemanticMetadata{
        redefines baseType=const_attributes meta SysML::AttributeUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def measureAttribute specializes SemanticMetadata{
        redefines baseType=measurement meta SysML::AttributeUsage;
        subsets annotatedElement : SysML::Usage;
       
    }

    metadata def Condition specializes SemanticMetadata{
        redefines baseType=LibTwinConditionAction meta SysML::ActionDefinition;
        subsets annotatedElement:SysML::Definition;
    }

    metadata def condition specializes SemanticMetadata{
        redefines baseType=strategies meta SysML::ActionUsage;
        subsets annotatedElement:SysML::Usage;
    }

    metadata def strategyAction specializes SemanticMetadata{
        redefines baseType=strategieActions meta SysML::PartUsage;
        subsets annotatedElement:SysML::Usage;

    }
}

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
                }
                #component p14:>>sensor;
            }
        }
       
        #database part TimeSeriesDB{
            :>> libTwinDataBaseTier default LibTwinDataBaseTier::HOT;
            :>> libTwinDataBaseType default LibTwinDataBaseType::TIMESERIES;
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
}