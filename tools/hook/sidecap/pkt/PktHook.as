package pkt
{
   import flash.external.ExternalInterface;
   import flash.utils.ByteArray;
   import flash.utils.IExternalizable;
   import flash.utils.describeType;
   import flash.utils.getQualifiedClassName;
   
   public class PktHook
   {
      
      public function PktHook()
      {
         super();
      }
      
      public static function reportOut(param1:*, param2:ByteArray) : void
      {
         report("out",param1,param2);
      }
      
      public static function reportIn(param1:*) : void
      {
         report("in",param1,null);
      }
      
      private static function report(param1:String, param2:*, param3:ByteArray) : void
      {
         var _loc4_:String = null;
         if(!hookOn())
         {
            return;
         }
         try
         {
            _loc4_ = dumpMsg(param2,0);
            ExternalInterface.call("__pkt",param1,shortName(param2),_loc4_,param3 != null ? toHex(param3) : "");
         }
         catch(e:Error)
         {
         }
      }
      
      private static function hookOn() : Boolean
      {
         if(!ExternalInterface.available)
         {
            return false;
         }
         try
         {
            return ExternalInterface.call("__pktOn") == true;
         }
         catch(e:Error)
         {
         }
         return false;
      }
      
      private static function shortName(param1:*) : String
      {
         var _loc2_:String = getQualifiedClassName(param1);
         var _loc3_:int = _loc2_.lastIndexOf("::");
         return _loc3_ >= 0 ? _loc2_.substr(_loc3_ + 2) : _loc2_;
      }
      
      private static function isMsg(param1:*) : Boolean
      {
         if(param1 == null || param1 is String || param1 is Number || param1 is Boolean || param1 is Array || param1 is ByteArray)
         {
            return false;
         }
         try
         {
            return param1 is IExternalizable;
         }
         catch(e:Error)
         {
         }
         return false;
      }
      
      private static function skipDumpName(param1:String) : Boolean
      {
         if(param1 == null || param1.length == 0)
         {
            return true;
         }
         if(param1 == "prototype" || param1 == "constructor")
         {
            return true;
         }
         if(param1.indexOf("remove") == 0)
         {
            return true;
         }
         if(param1 == "writeToBuffer" || param1 == "readFromBuffer" || param1 == "writeExternal" || param1 == "readExternal" || param1 == "toString")
         {
            return true;
         }
         return false;
      }
      
      private static function dumpVal(param1:*, param2:String, param3:int) : String
      {
         var _loc4_:Array = null;
         var _loc5_:int = 0;
         var _loc6_:int = 0;
         var _loc7_:int = 0;
         var _loc8_:Array = null;
         var _loc9_:* = undefined;
         var _loc10_:String = null;
         if(param1 == null)
         {
            return "";
         }
         if(param1 is Array)
         {
            _loc4_ = param1 as Array;
            if(_loc4_.length == 0)
            {
               return "";
            }
            _loc5_ = param2 == "bagItem" ? 700 : 200;
            _loc6_ = _loc4_.length < _loc5_ ? int(_loc4_.length) : _loc5_;
            _loc8_ = [];
            _loc7_ = 0;
            while(_loc7_ < _loc6_)
            {
               _loc9_ = _loc4_[_loc7_];
               if(_loc9_ == null)
               {
                  _loc8_.push("null");
               }
               else if(isMsg(_loc9_))
               {
                  _loc8_.push(dumpMsg(_loc9_,param3 + 1));
               }
               else
               {
                  _loc8_.push(String(_loc9_));
               }
               _loc7_++;
            }
            _loc10_ = "[" + _loc8_.join(",") + "]";
            if(_loc4_.length > _loc5_)
            {
               _loc10_ = _loc10_.substr(0,_loc10_.length - 1) + ",…共" + _loc4_.length + "项]";
            }
            return _loc10_;
         }
         if(isMsg(param1))
         {
            return dumpMsg(param1,param3 + 1);
         }
         return String(param1);
      }
      
      private static function dumpMsg(param1:*, param2:int) : String
      {
         var _loc3_:XML = null;
         var _loc4_:XML = null;
         var _loc5_:String = null;
         var _loc6_:String = null;
         var _loc7_:* = undefined;
         var _loc8_:String = null;
         var _loc9_:Array = null;
         if(param1 == null)
         {
            return "";
         }
         if(param2 > 6)
         {
            return shortName(param1) + "(…)";
         }
         _loc9_ = [];
         try
         {
            _loc3_ = describeType(param1);
            for each(_loc4_ in _loc3_.accessor)
            {
               _loc5_ = String(_loc4_.@name);
               _loc6_ = String(_loc4_.@access);
               if(!(skipDumpName(_loc5_) || _loc6_ == "writeonly"))
               {
                  try
                  {
                     _loc7_ = param1[_loc5_];
                  }
                  catch(e1:Error)
                  {
                     continue;
                  }
                  _loc8_ = dumpVal(_loc7_,_loc5_,param2);
                  if(!(_loc8_ == null || _loc8_.length == 0))
                  {
                     _loc9_.push(_loc5_ + "=" + _loc8_);
                  }
               }
            }
            for each(_loc4_ in _loc3_.variable)
            {
               _loc5_ = String(_loc4_.@name);
               if(!skipDumpName(_loc5_))
               {
                  try
                  {
                     _loc7_ = param1[_loc5_];
                  }
                  catch(e2:Error)
                  {
                     continue;
                  }
                  _loc8_ = dumpVal(_loc7_,_loc5_,param2);
                  if(!(_loc8_ == null || _loc8_.length == 0))
                  {
                     _loc9_.push(_loc5_ + "=" + _loc8_);
                  }
               }
            }
         }
         catch(e:Error)
         {
         }
         return shortName(param1) + "(" + _loc9_.join(";") + (_loc9_.length > 0 ? ";" : "") + ")";
      }
      
      private static function toHex(param1:ByteArray) : String
      {
         var _loc2_:uint = 0;
         var _loc3_:String = null;
         var _loc4_:String = "";
         var _loc5_:uint = param1.position;
         param1.position = 0;
         while(param1.bytesAvailable)
         {
            _loc2_ = param1.readUnsignedByte();
            _loc3_ = _loc2_.toString(16);
            if(_loc3_.length < 2)
            {
               _loc3_ = "0" + _loc3_;
            }
            _loc4_ += _loc3_;
         }
         param1.position = _loc5_;
         return _loc4_;
      }
   }
}
