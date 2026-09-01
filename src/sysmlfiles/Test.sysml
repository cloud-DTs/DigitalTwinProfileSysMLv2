package MGrid {

    private import MetaModelDigitalTwin::*;

    #Component def PAC_Sensor {
        
    }
    #Entity def Battery{
        #component sensor: PAC_Sensor{
            #measureAttribute totalCapacity {
                    :>> dataType default AttributeDataType::INTEGER;
                }
        }
        
    }

    #Entity def PV{
        #component sensor: PAC_Sensor{
            #measureAttribute output{
                    :>> dataType default AttributeDataType::DOUBLE;
                }
            }
        
    }

    #Condition def StopCharging{
        #strategyAction stopCharging :>>strategieActions{
        :>> name = "StopCharging";
        :>> strategyType = StrategyType::LAMBDA;
        :>> pathToCode = "/home/marco/HackathonSysmlv2DemoRepository/digital-twin-manager/lambda_functions/event_actions/high-temperature-callback";
        :>> external = false;
        }
    }

    #Entity def Charger{
        #constAttribute maxConsumption {
            :>> value default "50.0";
            :>>dataType default AttributeDataType::DOUBLE;
        }
        #component sensor: PAC_Sensor;
    }

     

    #Twin def MGrid {
            #entity battery : Battery{

                p16:>>sensor;
            }
            #entity KebaP30 : Charger{
                :>>maxConsumption {
                    :>> value default "15.0";
                }
                p13 :>> sensor{
                    #measureAttribute power {
                    :>> dataType default AttributeDataType::DOUBLE;
                    }
                }
            }
            #entity SieVersicharge :Charger{

                p14 :>> sensor{
                    #measureAttribute consumption {
                    :>> dataType default AttributeDataType::DOUBLE;
                    }
                }
            }
            #entity SieChargeCC: Charger{
                p12 :>> sensor{
                    #measureAttribute consumption {
                    :>> dataType default AttributeDataType::DOUBLE;
                    }
                }
            }
            #entity pv : PV{
                pV1 :>> sensor;
            }
            #entity SieChargeD : Charger{
                p17 :>> sensor{
                    #measureAttribute consumption {
                    :>> dataType default AttributeDataType::DOUBLE;
                    }
                }
            }
            #entity SieCPC20 : Charger{
                p11 :>> sensor{
                    #measureAttribute consumption {
                    :>> dataType default AttributeDataType::DOUBLE;
                    }
                }
            }
    
        :>>hotDatabaseRetentionDays default 30;
        :>>coldDatabaseRetentionDays default 30;

        #condition stopCharging :StopCharging{
            :>>leftOperand = KebaP30.p13.power;
            :>>operator = ComparisonOperator::EQUAL;
            :>>rightOperand = KebaP30.maxConsumption;
            :>>stopCharging{
                :>> feedbackTopicType = FeedbackTopicType::INTERN;
                :>> componentTopic = KebaP30.p13;
                test2:> inputParameters = KebaP30.p13.power;
                test3:> inputParameters = KebaP30.p13.power;
               test4:>outputParameters = KebaP30.p13.power;
              
            }
        }
    
    }
    
}