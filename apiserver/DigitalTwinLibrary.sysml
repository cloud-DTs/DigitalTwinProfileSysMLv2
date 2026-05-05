library package DigitalTwinLibrary{

    abstract part libTwinEntities:LibTwinEntity[0..*];
    
    abstract attribute libTwinDataBaseType:LibTwinDataBaseType;
    abstract attribute retentionDays:ScalarValues::Integer;
    abstract part def LibTwin{
        abstract part redefines libTwinEntities;
        abstract attribute hotDatabaseType redefines libTwinDataBaseType default LibTwinDataBaseType::RELATIONAL;
        abstract attribute hotDatabaseRetentionDays redefines retentionDays default 30;
        abstract attribute coldDataBaseType redefines libTwinDataBaseType default LibTwinDataBaseType::RELATIONAL;
        abstract attribute coldDatabaseRetentionDays redefines retentionDays default 30;
       
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
    abstract attribute measurements:LibDTAttributes[0..*];
    abstract part def LibTwinComponent{
        abstract attribute redefines measurements;
    }
   
   
    abstract attribute leftOperand:LibDTAttributes;
    abstract attribute operator:ComparisonOperator;
    abstract attribute rightOperand:LibDTAttributes;
    abstract part strategieActions:LibTwinStrategyAction[0..*];
    
    
    abstract action def LibTwinConditionAction{
        abstract attribute redefines leftOperand;
        abstract attribute redefines operator;
        abstract attribute redefines rightOperand;
        abstract part redefines strategieActions;
    }
    abstract attribute name:ScalarValues::String;
    abstract attribute description:ScalarValues::String;
    abstract attribute pathToCode:ScalarValues::String;
    abstract attribute external:ScalarValues::Boolean;
    abstract attribute strategyType:StrategyType;
 
    abstract attribute customPayload:ScalarValues::String;
    abstract part componentTopic:LibTwinComponent;
    abstract attribute externalTopic:ScalarValues::String;
    abstract attribute useExternalTopic:ScalarValues::Boolean;
    abstract attribute feedbackTopicType:FeedbackTopicType;
    abstract attribute inputParameters:LibDTAttributes[0..*];
    abstract attribute constInputParameters:ConstAttributes[0..*];
    abstract attribute outputParameters:AttributeDataType[0..*];
 
    abstract part def LibTwinStrategyAction{
        abstract attribute redefines name;
        abstract attribute redefines description;
        abstract attribute redefines external default true;
        abstract attribute redefines pathToCode;
        abstract attribute redefines inputParameters;
        abstract attribute redefines constInputParameters;
        abstract attribute redefines outputParameters;
        abstract attribute redefines strategyType default StrategyType::LAMBDA;
        abstract attribute redefines customPayload;
        abstract attribute redefines feedbackTopicType default FeedbackTopicType::NOFEEDBACK;
        abstract part redefines componentTopic;
        abstract attribute redefines externalTopic;
    }


    
    
    enum def AttributeDataType{
        STRING;
        DOUBLE;
        INTEGER;
    }
    
    enum def FeedbackTopicType{
        EXTERN;
        INTERN;
        NOFEEDBACK;
    }
    attribute def LibDTAttributes{
        attribute dataType:AttributeDataType default AttributeDataType::STRING;
    }

    attribute def ConstAttributes specializes LibDTAttributes{
        attribute value:ScalarValues::String;
    }

    enum def LibTwinDataBaseType{
        RELATIONAL;
        TIMESERIES;
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
    }

}
