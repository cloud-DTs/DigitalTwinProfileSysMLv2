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
        in abstract attribute redefines leftOperand;
        abstract attribute redefines operator;
        in abstract attribute redefines rightOperand;
        out abstract attribute redefines result;
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
