library package DigitalTwinLibrary {

    part def TwinEntity {
        part redefines subEntities;
        part redefines twinComponents;
        attribute redefines const_attributes;
    }

    
    part def TwinComponent {
        out port redefines measurementPorts;
    }


    attribute def Property {
        attribute redefines dataType;
    }

    port def MeasurementPort {
        out attribute redefines measurement;
    }

    attribute def ConstProperty :> Property {
        attribute value : ScalarValues::String default ="";
    }
    
    interface def MeasurementInterface {
        
        end redefines sourceMeasurementPort;
        end redefines targetMeasurementPort;
    }

    part def TwinDataBase{
        attribute redefines dataBaseTier;
        attribute redefines dataBaseType;
        port redefines measurementDataBasePorts;
    }

    enum def AttributeDataType {
        INTEGER;
        DOUBLE;
        STRING;
    }
    enum def MeasurementInterFaceType{
        MQTT;
    }

    enum def DataBaseTier{
        HOT;
        COLD;
    }   

    enum def DataBaseType{
        TIMSERIES;
        RELATIONAL;
    }


    attribute const_attributes : ConstProperty [0..*];
    part subEntities : TwinEntity [0..*];
    part twinComponents   : TwinComponent  [0..*];
    port measurementPorts : MeasurementPort [0..*];
    port measurementDataBasePorts : ~MeasurementPort [0..*];
    attribute dataType : AttributeDataType;
    end[0..*] port sourceMeasurementPort : MeasurementPort;
    end[0..*] port targetMeasurementPort:MeasurementPort;
    port targetPort : ~MeasurementPort;
    part entities : TwinEntity [0..*];
    attribute measurementInterFaceType:MeasurementInterFaceType;
    abstract interface measurementConnections:MeasurementInterface[0..*];
    part twinDataBases:TwinDataBase[2..*];
    attribute dataBaseTier:DataBaseTier;
    attribute dataBaseType:DataBaseType;
    out attribute measurement : Property;
    
    
    part def Twin {
        part redefines entities;
        part redefines measurementConnections;
        part redefines twinDataBases;

        
    }
}

