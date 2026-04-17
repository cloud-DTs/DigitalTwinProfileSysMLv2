package MG {

    private import MetaModelDigitalTwin::*;

    #Component def PAC_Sensor {
        #measureAttribute consumption {
            :>> dataType default AttributeDataType::DOUBLE;
        }
        attribute test;
    }

    abstract #Entity def AbstractEntity {
        #constAttribute maxConsumption {
            value2 :>> value default "23.0";
            :> dataType default AttributeDataType::DOUBLE;
        }
        #component sensor : PAC_Sensor;
    }

    abstract #Entity def IntermediateBattery :> AbstractEntity {
        #constAttribute :>> maxConsumption {
            :>> value2 default "10.0";
        }
    }

    abstract #Entity def Battery :> IntermediateBattery {
        #constAttribute :>> maxConsumption {
            :>> value2 default "5.0";
        }
        #component batterySensor :>> sensor;
        #component inverter : PAC_Sensor;
        part testNotIncuded;
    }

 
    #Twin def MGTwin {
        
        #entity MicroGrid {
            

            #entity battery : Battery {
                mComp :>> maxConsumption {
                    :>> value2 = "3.0";
                }
                
                internalInverter :> inverter; 
                
                test :> test;

                #component p12 :>> batterySensor;
            }

            #entity sieVercharge : AbstractEntity {
                #component p13 :>> sensor;
            }

            #entity kebaP30 : AbstractEntity {
                #constAttribute :>> maxConsumption {
                }
                #component p14 :>> sensor;
            }


            #entity edgeCaseNode : AbstractEntity {
               
            }
        }

        #condition CheckBatteryConsumption {
            :>> operator = ComparisonOperator::GREATER_THAN;
            
            :>> leftOperand  = MicroGrid.sieVercharge.p13.consumption;
        
            :>> rightOperand = MicroGrid.battery.mComp;
            #strategyAction alertAction {
                :>> name = "Alert Action";
                :>> strategyType = StrategyType::LAMBDA;
                :>> description = "Alerts when battery consumption is too high";
                :>> pathToCode = "/home/marcocotrotzo/PycharmProjects/digital-twin-manager/lambda_functions/event_actions/high-temperature-callback";
                :>> external = false;
                :>> feedbackTopicType = FeedbackTopicType::EXTERN;
                :>> externalTopic = "EXTERN_TPIC";
                :>> customPayload = "{\"message\":\"High Consumption Alert\"}";
            }

            #strategyAction alertAction2 {
                :>> name = "Internal Correction";
                :>> strategyType = StrategyType::LAMBDA;
                :>> description = "Feedback to battery sensor";
                :>> pathToCode = "";
                :>> external = true;
                :>> feedbackTopicType = FeedbackTopicType::INTERN;
                :>> componentTopic = MicroGrid.battery.p12;
            }

            #strategyAction alertAction3 {
                :>> name = "Log Action";
                :>> strategyType = StrategyType::LAMBDA;
                :>> external = true;
            }
        }
    }
}