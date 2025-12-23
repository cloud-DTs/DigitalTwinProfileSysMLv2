package Publish {

    library package DigitalTwinLibrary{

    abstract part libTwinEntities:LibTwinEntity[0..*];
    abstract part dataBases:LibTwinDataBase[0..*];
    abstract interface measurementInterfaces:MeasurementInterface[0..*];
    abstract part def LibTwin{
        abstract part redefines libTwinEntities;
        abstract part redefines dataBases;
        abstract interface redefines measurementInterfaces;
    }
    abstract attribute const_attributes:ConstAttributes[0..*];
    abstract part sbEntities:LibTwinEntity[0..*];
    abstract part cmponents:LibTwinComponent[0..*];
    abstract action strategies:LibTwinConditionAction[0..*];
    
    abstract part def LibTwinEntity{
        abstract attribute redefines const_attributes;
        abstract part redefines sbEntities;
        abstract part redefines cmponents;
        abstract action redefines strategies;
        

    }
    
    out abstract port measurements:MeasurePort[0..*];
    abstract part def LibTwinComponent{
        out abstract port measures redefines measurements;
    }
    abstract attribute libTwinDataBaseTier:LibTwinDataBaseTier;
    abstract attribute libTwinDataBaseType:LibTwinDataBaseType;
    in abstract port dataBaseInPort:~MeasurePort;
    abstract part def LibTwinDataBase{
        abstract attribute redefines libTwinDataBaseTier;
        abstract attribute redefines libTwinDataBaseType;
        in abstract port redefines dataBaseInPort;
    }
    abstract attribute type:MeasurementInterfaceType;
    abstract interface def MeasurementInterface{
        abstract attribute redefines type; 
        end source : MeasurePort;
        end target : ~MeasurePort;
    }
    abstract attribute leftOperand:LibDTAttributes;
    abstract attribute operator:ComparisonOperator;
    abstract attribute rightOperand:LibDTAttributes;
    abstract attribute result:ScalarValues::Boolean;
    abstract part strategieActions:LibTwinStrategyAction[0..*];
    abstract action def LibTwinConditionAction{
        abstract attribute redefines leftOperand;
        abstract attribute redefines operator;
        abstract attribute redefines rightOperand;
        abstract attribute redefines result;
        abstract part redefines strategieActions;
    }
    abstract attribute name:ScalarValues::String;
    abstract attribute description:ScalarValues::String;
    abstract attribute pathToCode:ScalarValues::String;
    abstract attribute strategyType:StrategyType;
    abstract part def LibTwinStrategyAction{
        abstract attribute redefines name;
        abstract attribute redefines description;
        abstract attribute redefines pathToCode;
        abstract attribute redefines strategyType;
    }

    enum def AttributeDataType{
        STRING;
        DOUBLE;
        INTEGER;
    }
    attribute def LibDTAttributes{
        attribute dataType:AttributeDataType;
    }

    attribute def ConstAttributes specializes LibDTAttributes{
        attribute value:ScalarValues::String;
    }
    
    abstract attribute measurement:LibDTAttributes[0..*];
    port def MeasurePort{
        abstract attribute redefines measurement;
    }



    enum def LibTwinDataBaseTier{
        HOT;
        COLD;
    }

    enum def LibTwinDataBaseType{
        RELATIONAL;
        TIMESERIES;
    }

    enum def MeasurementInterfaceType{
        MQTT;
        REST;
        GRPC;
    }

    enum def ComparisonOperator{
        GREATER_THAN;
        LESS_THAN;
        EQUAL;
        GREATER_EQUAL;
        LESS_EQUAL;
        NOT_EQUAL;
    }
    enum def StrategyType{
        LAMBDA;
        CONTAINER;
    }

}

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
}