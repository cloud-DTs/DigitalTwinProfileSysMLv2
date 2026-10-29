package MGrid {

    private import MetaModelDigitalTwin::*;

    #Component def PAC_Sensor { }

    #Component def BatteryController { }

    #Entity def Battery {
        #component sensor : PAC_Sensor {
            #measureAttribute totalCapacity {
                :>> dataType default AttributeDataType::INTEGER;
            }
            #measureAttribute power {
                :>> dataType default AttributeDataType::DOUBLE;
            }
        }
        #component controller : BatteryController;
    }

    #Entity def PV {
        #component sensor : PAC_Sensor {
            #measureAttribute output {
                :>> dataType default AttributeDataType::DOUBLE;
            }
        }
    }

    #Entity def Charger {
        #constAttribute maxConsumption {
            :>> value default "50.0";
            :>> dataType default AttributeDataType::DOUBLE;
        }
        #component sensor : PAC_Sensor {
            #measureAttribute power {
                :>> dataType default AttributeDataType::DOUBLE;
            }
            #measureAttribute consumption {
                :>> dataType default AttributeDataType::DOUBLE;
            }
        }
    }

    #Condition def ChargerChanged {
        #strategyAction balance :>> strategieActions {
            :>> name = "Balance";
            :>> strategyType = StrategyType::LAMBDA;
            :>> pathToCode = "lambda_functions/event_actions/energy-management";
            :>> external = false;
            :>> feedbackTopicType = FeedbackTopicType::INTERN;
        }
    }

    #Condition def ChargerChanged2 {

        }

    #Twin def MGrid {
        #entity MicroGrid {
            #constAttribute chargingThreshold {
                :>> value default "0.0";
                :>> dataType default AttributeDataType::DOUBLE;
            }

            #entity battery : Battery { p16 :>> sensor; }
            #entity pv : PV { pV1 :>> sensor; }

            #entity charger1 : Charger {
                :>> maxConsumption { :>> value default "15.0"; }
                p13 :>> sensor;
            }
            #entity charger2 : Charger { p14 :>> sensor; }
            #entity charger3 : Charger { p12 :>> sensor; }
            #entity charger4 : Charger { p17 :>> sensor; }
            #entity charger5 : Charger { p11 :>> sensor; }
        }

        :>> hotDatabaseRetentionDays default 30;
        :>> coldDatabaseRetentionDays default 30;

        #condition charger1Changed : ChargerChanged2 {
            :>> leftOperand = MicroGrid.charger1.p13.power;
            :>> operator = ComparisonOperator::GREATER_THAN;
            :>> rightOperand = MicroGrid.chargingThreshold;

        }
        #condition charger2Changed : ChargerChanged {
            :>> leftOperand = MicroGrid.charger2.p14.power;
            :>> operator = ComparisonOperator::GREATER_THAN;
            :>> rightOperand = MicroGrid.chargingThreshold;
            balance2 :>> balance {
                :>> componentTopic = MicroGrid.battery.controller;
            }
        }
        #condition charger3Changed : ChargerChanged {
            :>> leftOperand = MicroGrid.charger3.p12.power;
            :>> operator = ComparisonOperator::GREATER_THAN;
            :>> rightOperand = MicroGrid.chargingThreshold;
            balance3 :>> balance {
                :>> componentTopic = MicroGrid.battery.controller;
            }
        }
        #condition charger4Changed : ChargerChanged {
            :>> leftOperand = MicroGrid.charger4.p17.power;
            :>> operator = ComparisonOperator::GREATER_THAN;
            :>> rightOperand = MicroGrid.chargingThreshold;
            balance4 :>> balance {
                :>> componentTopic = MicroGrid.battery.controller;
            }
        }
        #condition charger5Changed : ChargerChanged {
            :>> leftOperand = MicroGrid.charger5.p11.power;
            :>> operator = ComparisonOperator::GREATER_THAN;
            :>> rightOperand = MicroGrid.chargingThreshold;
            balance5 :>> balance {
                :>> componentTopic = MicroGrid.battery.controller;
            }
        }
    }
}
