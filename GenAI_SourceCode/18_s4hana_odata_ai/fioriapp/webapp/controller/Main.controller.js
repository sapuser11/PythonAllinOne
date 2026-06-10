sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/m/MessageToast",
    "sap/ui/model/json/JSONModel"
], function (Controller, MessageToast,  JSONModel) {
    "use strict";

    return Controller.extend("anubhav.ai.controller.Main", {
        onInit: function () {
            // Initialize JSON model to hold input and response
            this.oModel = new JSONModel({
                userInput: "",
                apiResponse: "",
                additionalData: {}
            });
            
            this.getView().setModel(this.oModel, "appModel");
        },

        onSendRequest: function () {
            var oModel = this.getView().getModel("appModel");
            var sUserInput = oModel.getProperty("/userInput");
            
            // Check if input is not empty
            if (!sUserInput || sUserInput.trim() === "") {
                MessageToast.show("Please enter a message first");
                return;
            }

            // Show loading indicator
            sap.ui.core.BusyIndicator.show();

            // Prepare payload
            var oPayload = {
                message: sUserInput
            };

            // Add the user message to the chat history
            var oChatList = this.getView().byId("chatBot");
            if (oChatList) {
                // Create a new feed list item for user's message
                var oFeedListItem = new sap.m.FeedListItem({
                    sender: "You",
                    icon: "sap-icon://person-placeholder",
                    timestamp: new Date().toLocaleString(),
                    text: sUserInput,
                    convertLinksToAnchorTags: "All"
                });
                
                // Add the item to the list
                oChatList.addItem(oFeedListItem);
                
                // Scroll to the bottom of the list
                setTimeout(function() {
                    var oListDomRef = oChatList.getDomRef();
                    if (oListDomRef) {
                        oListDomRef.scrollTop = oListDomRef.scrollHeight;
                    }
                }, 100);
            }
            debugger;
            // Check if the user is requesting to see data
            if (sUserInput.trim() === "/data") {
                // Clear the input field
                //this.clearInput();
                
                // Get additional data from model
                var oAdditionalData = this.oModel.getProperty("/additionalData");
                // Check if oAdditionalData and d property exist
                if (!oAdditionalData || !oAdditionalData.data || !oAdditionalData.data.d) {
                    sFormattedData = "No data available";
                } else {
                    // Extract only the required fields from oAdditionalData.data.d
                    var extractedData = {
                        SalesOrder: oAdditionalData.data.d.SalesOrder,
                        SalesOrganization: oAdditionalData.data.d.SalesOrganization,
                        DistributionChannel: oAdditionalData.data.d.DistributionChannel,
                        SoldToParty: oAdditionalData.data.d.SoldToParty,
                        TotalNetAmount: oAdditionalData.data.d.TotalNetAmount,
                        OverallDeliveryStatus: oAdditionalData.data.d.OverallDeliveryStatus
                    };
                    
                    // Format data as simple text with line breaks
                    var sFormattedData = "Sales Order: " + extractedData.SalesOrder + "\n" +
                                        "Sales Organization: " + extractedData.SalesOrganization + "\n" +
                                        "Distribution Channel: " + extractedData.DistributionChannel + "\n" +
                                        "Sold To Party: " + extractedData.SoldToParty + "\n" +
                                        "Total Net Amount: " + extractedData.TotalNetAmount + "\n" +
                                        "Overall Delivery Status: " + extractedData.OverallDeliveryStatus;
                }

                //var sFormattedData = JSON.stringify(oAdditionalData, null, 2);
                
                // Add the data as a new feed list item
                if (oChatList) {
                    var oDataFeedItem = new sap.m.FeedListItem({
                        sender: "Bot",
                        icon: "sap-icon://ai",
                        timestamp: new Date().toLocaleString(),
                        text:  sFormattedData
                    });
                    debugger;
                    oChatList.addItem(oDataFeedItem);
                    
                    // Scroll to the bottom of the list
                    setTimeout(function() {
                        var oListDomRef = oChatList.getDomRef();
                        if (oListDomRef) {
                            oListDomRef.scrollTop = oListDomRef.scrollHeight;
                        }
                    }, 100);
                }
                
                // Stop further processing for this request
                sap.ui.core.BusyIndicator.hide();
                return;
            }

            // Call REST API
            var that = this;
            $.ajax({
                url: "/chat",   // your REST API
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify(oPayload),   // send data as JSON string
                success: function(oResponse) {
                    // Create model with response
                    
                    that.oModel.setProperty("/apiResponse", oResponse.response )
                    that.oModel.setProperty("/additionalData", oResponse.data)
                    sap.ui.core.BusyIndicator.hide();
                    if (oChatList) {
                                    // Create a new feed list item for user's message
                                    var oFeedListItem = new sap.m.FeedListItem({
                                        sender: "Bot",
                                        icon: "sap-icon://ai",
                                        timestamp: new Date().toLocaleString(),
                                        text: oResponse.response + "\n type /data to see additionalData",
                                        convertLinksToAnchorTags: "All"
                                    });
                                    
                                    // Add the item to the list
                                    oChatList.addItem(oFeedListItem);
                                    
                                    // Scroll to the bottom of the list
                                    setTimeout(function() {
                                        var oListDomRef = oChatList.getDomRef();
                                        if (oListDomRef) {
                                            oListDomRef.scrollTop = oListDomRef.scrollHeight;
                                        }
                                    }, 100);
                                }
                    //sap.m.MessageToast.show("POST successful!");
                }.bind(this),
                error: function(oError) {
                    sap.m.MessageToast.show("POST failed!");
                    console.error("Error in POST:", oError);
                }
            });
        },

        clearInput: function() {
            var oModel = this.getView().getModel("appModel");
            oModel.setProperty("/userInput", "");
        },

        clearResponse: function() {
            var oModel = this.getView().getModel("appModel");
            oModel.setProperty("/apiResponse", "");
        }
    });
});