package MicroGridExample{

    private import MetaModelDigitalTwin::*;

    #Component def PAC_Sensor{
            #measureAttribute consumption {
                    :>> dataType default AttributeDataType::DOUBLE;
            }
          
            attribute test;
         
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
                
                #component p13:>>sensor;
            }
            #entity kebaP30:AbstractEntity{
                #constAttribute :>> maxConsumption{
                }
                #component p14:>>sensor;
            }
        }
        
        #condition CheckBatteryConsumption{
            :>> operator = ComparisonOperator::GREATER_THAN;
            :>> leftOperand  = MicroGrid.sieVercharge.p13.consumption;
            :>> rightOperand = MicroGrid.battery.maxConsumption;
            #strategyAction alertAction{
                :>> name = "Alert Action";
                :>> strategyType = StrategyType::LAMBDA;
                :>> description = "Alerts when battery consumption is too high";
                :>> pathToCode = "\\path\\to\\alertFunction";
                :>> external = true;
                :>> feedbackTopicType = FeedbackTopicType::EXTERN;
                :>> externalTopic = "EXTERN_TPIC";
                :>>customPayload = "{\"message\":\"HelloWordl\"}";
                
            }
            #strategyAction alertAction2{
                :>> name = "Alert Action";
                :>> strategyType = StrategyType::LAMBDA;
                :>> description = "Alerts when battery consumption is too high";
                :>> pathToCode = "";
                :>> external = false;
                :>> feedbackTopicType = FeedbackTopicType::INTERN;
                :>> componentTopic = MicroGrid.battery.p12;
            }
            
            #strategyAction alertAction3{
                :>> name = "Alert Action";
                :>> strategyType = StrategyType::LAMBDA;
                :>> description = "Alerts when battery consumption is too high";
                :>> pathToCode = "";
                :>> external = false;
                
            }
        }
    }
}
               