/* ************************************************************************

   Copyright:
     2012 1&1 Internet AG, Germany, http://www.1und1.de

   Authors:
     * Mustafa Sak (msak)


************************************************************************ */

/**
 * Registrar for command groups to be able to active or deactive them.
 */
qx.Class.define("qx.ui.command.GroupManager",
{
  extend : qx.core.Object,


  construct : function()
  {
    this.base(arguments);
    this.__groups = [];
  },


  members :
  {
    __groups: null,
    __activeGroup : null,


    /**
     * Add command group.
     * @param group {qx.ui.command.Group} Command group
     */
    add : function(group)
    {
      if (qx.core.Environment.get("qx.debug")) {
        this.assertInstance(group, qx.ui.command.Group, "Given group is not an instance of qx.ui.command.Group");
      }

      if (qx.lang.Array.contains(this.__groups, group)){
        this.debug("Group is already added!");
        return;
      }

      this.__groups.push(group);

      // deactivate added group to prevent collusions
      group.setActive(false);
    },


    /**
     * Activates a command group and deactiveted all others.
     *
     * @param group {qx.ui.command.Group} Command group
     */
    setActive : function(group)
    {
      if (qx.core.Environment.get("qx.debug")) {
        this.assertInstance(group, qx.ui.command.Group, "Given group is not an instance of qx.ui.command.Group");
      }

      if (!this.has(group)){
        this.debug("Group was not added before! You have to use 'addCommand()' method before activating!");
        return;
      }

      // iterate through all groups and deactivate all expect the given one
      for (var i=0; i<this.__groups.length; i++)
      {
        var item = this.__groups[i];
        if (item == group){
          item.setActive(true);
          this.__activeGroup = item;
          continue;
        }
        item.setActive(false);
      }
    },


    /**
     * Returns active command group.
     *
     * @return {qx.ui.command.Group} Active command group
     */
    getActive : function()
    {
      return this.__activeGroup;
    },


    /**
     * Blocks the active command group.
     */
    block : function()
    {
      if(this.__activeGroup){
        this.__activeGroup.setActive(false);
      }
    },


    /**
     * Unblocks the active command group.
     */
    unblock : function()
    {
      if(this.__activeGroup){
        this.__activeGroup.setActive(true);
      }
    },


    /**
     * Helper function returns added command group.
     *
     * @param group {qx.ui.command.Group} Command group
     *
     * @return {qx.ui.command.Group | null} Command group or null
     */
    _getGroup : function(group)
    {
      var index = this.__groups.indexOf(group);
      if (index === -1){
        return null;
      }
      return this.__groups[index];
    },


    /**
     * Whether a command manager was added.
     *
     * @param group {qx.ui.command.Group} Command group
     *
     * @return {Boolean} <code>true</code> if group already added
     */
    has : function(group)
    {
      if (qx.core.Environment.get("qx.debug")) {
        this.assertInstance(group, qx.ui.command.Group, "Given group is not an instance of qx.ui.command.Group");
      }

      return !!(this._getGroup(group));
    }
  },


  destruct : function()
  {
     this.__groups = this.__activeGroup = null;
  }
});
