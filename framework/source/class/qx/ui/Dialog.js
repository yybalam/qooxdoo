/* ************************************************************************

   qooxdoo - the new era of web development

   http://qooxdoo.org

   Copyright:
     2017 Yeshua Rodas, http://yybalam.net

   License:
     MIT: https://opensource.org/licenses/MIT
     See the LICENSE file in the project's top-level directory for details.

   Authors:
     * Yeshua Rodas (yybalam)

************************************************************************ */

qx.Bootstrap.define("qx.ui.Dialog",
{
  type: "static",

  statics : {
    messageBox: function(options) {
      var caption, message, icon;

      if (qx.lang.Type.isString(options)) {
        message = options;
        caption = caption || "Alert";
        icon = icon || "alert";

        (new qx.ui.dialog.Message(caption, message, icon)).open();
      }
      else if (qx.lang.Type.isObject(options)) {
        (new qx.ui.dialog.Message(options['caption'], options['message'], options['icon'])).open();
      }
    },

    alert: function (message) {
      (new qx.ui.dialog.Message(qx.locale.Manager.tr("Alert"), message, "alert")).open();
    },

    error: function(message) {
      (new qx.ui.dialog.Message(qx.locale.Manager.tr("Error"), message, "error")).open();
    },

    warning: function (message) {
      (new qx.ui.dialog.Message(qx.locale.Manager.tr("Warning"), message, "warning")).open();
    },

    success: function(message) {
      (new qx.ui.dialog.Message(qx.locale.Manager.tr("Success"), message, "success")).open();
    },

    /**
     * This method create and shown a confirm dialog.
     * @return {qx.ui.dialog.Confirm}
     */
    confirm: function(options) {
      var caption, message, buttons, icon;

      if (qx.lang.Type.isString(options)) {
        message = options;
        caption = qx.locale.Manager.tr("Confirm");
      }
      else if (qx.lang.Type.isObject(options)) {
        message = options['message'] || '';
        caption = options['caption'] || qx.locale.Manager.tr("Confirm");
        buttons = options['buttons'] || null;
        icon = options['icon'] || null;
      }
      else {
        throw new Error('Malformed arguments for confirm dialog.');
      }

      var dialog = new qx.ui.dialog.Confirm(caption, message, buttons, icon);
      dialog.open();
      return dialog;
    }
  }
});
