/**
 * This class is the controller for the main view for the application. It is specified as
 * the "controller" of the Main view class.
 *
 * TODO - Replace this content of this view to suite the needs of your application.
 */
Ext.define('command.view.main.MainController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.main',

    onLogoutClick: function () {
        Ext.Ajax.request({
            url: 'do_logout/',
            success: function (response) {
                window.location.reload();
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    exportRawData: function(b) {
        var main = Ext.ComponentQuery.query('#main_panel')[0];
        var panel = b.up('#experiment_search_result');
        var operation = 'export_raw_data';
        var request = main.getRequestObject(operation);
        request.view = 'export_data';
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    Ext.MessageBox.show({
                        title: 'Export raw data',
                        msg: 'Raw data TSV (gzip compressed) file will be created in background. Please check the Log Message panel to see when the file is ready.',
                        buttons: Ext.MessageBox.OK,
                        icon: Ext.MessageBox.INFO,
                        fn: function () {
                        }
                    });
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onFocusCompendium: function( me, event, eOpts ) {
        var ws = command.current.ws;
        var main = Ext.ComponentQuery.query('#main_panel')[0];
        var operation = 'read_compendia';
        var request = main.getRequestObject(operation);
        request.view = 'compendia';
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                me.store.loadData(action.data.compendia, false);
            }
        });
        ws.stream(request.view).send(request);
    },

    mainAfterRender: function ( me, eOpts ) {
        var compendium = JSON.parse(localStorage.getItem("current_compendium"));
        if (!compendium) {
            me.down('#data_collection_menu_item').disable();
            me.down('#annotation_menu_item').disable();
            me.down('#normalization_menu_item').disable();
        }
    },

    onSelectCompendium: function( me, record, eOpts ) {
        var main = Ext.ComponentQuery.query('#main_panel')[0];
        var mainTab = Ext.ComponentQuery.query('#main_tab_panel')[0];
        console.log(record.data);
        localStorage.setItem("current_compendium", JSON.stringify(record.data));
        main.down('#data_collection_menu_item').enable();
        main.down('#annotation_menu_item').enable();
        main.down('#normalization_menu_item').enable();
        mainTab.items.items.forEach(function (p) {
            var pName = p.itemId;
            var glyph = p.glyph;
            p.close();
            mainTab.up('#main_panel').controller.openPanel(pName, glyph);
        });
    },

    onTabChange: function(tabPanel, newTab, oldTab, index) {
        var url = "view/" + newTab.xtype;
        if (newTab.command_params) {
            url += "/" + newTab.command_params;
        }
        this.redirectTo(url);
        mainTab = Ext.ComponentQuery.query('#main_tab_panel')[0];
        var isAdminPanel = command.current.admin_panels.indexOf(newTab.itemId) != -1;
        if (isAdminPanel) {
            mainTab.setTitle('Admin');
        } else {
            if (newTab.itemId == "welcome") {
                mainTab.setTitle('Welcome to COMMAND');
            } else {
                var comp = JSON.parse(localStorage.getItem("current_compendium"));
                mainTab.setTitle('Compendium: ' + comp.compendium_name);
            }
        }
    },

    onMenuBeforeShow: function (menu, e, eOpts) {
        menu.down('menu').down('#experiments_menu_item').setDisabled(true);
        menu.down('menu').down('#platforms_menu_item').setDisabled(true);
        var comp = {compendium: localStorage.getItem("current_compendium")};
        Ext.Ajax.request({
            url: 'check_bio_features/',
            params: comp,
            success: function (response) {
                var resp = JSON.parse(response.responseText);
                var bioFeature = resp.bio_features;
                menu.down('menu').down('#experiments_menu_item').setDisabled(!bioFeature);
                menu.down('menu').down('#platforms_menu_item').setDisabled(!bioFeature);
            },
            failure: function (response) {
                console.log('Server error', response);
            }
        });
    },

    onAction: function (menu, e, eOpts) {
        this.redirectTo(eOpts.hash, true);
    },

    openPanel: function (panel, glyph, params) {
        var activeIndex = 0;
        mainTab = Ext.ComponentQuery.query('#main_tab_panel')[0];
        var isAdminPanel = command.current.admin_panels.indexOf(panel) != -1;
        var isWelcomePanel = panel == "welcome";
        var create_multiple_panel = command.current.panel_multi_instances.indexOf(panel) != -1;
        var itemId = panel;
        if (create_multiple_panel) {
            itemId += '_' + params;
        }
        var userTab = Ext.ComponentQuery.query('#' + itemId)[0];
        if (!userTab) {
            userTab = Ext.ComponentManager.create({
                xtype: panel,
                itemId: itemId,
                command_params: params,
                closable: true,
                glyph: glyph,
                border: false
            });
        } else {
            activeIndex = mainTab.items.indexOf(userTab);
        }
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        if (isAdminPanel || isWelcomePanel || (comp && comp.id)) {
            mainTab.insert(activeIndex, userTab);
        } else {
            this.redirectTo('#view/welcome', true);
            userTab.destroy();
        }
        mainTab.setActiveTab(activeIndex);
    }
});
