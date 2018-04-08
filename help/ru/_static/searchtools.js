/*
 * searchtools.js_t
 * ~~~~~~~~~~~~~~~~
 *
 * Sphinx JavaScript utilities for the full-text search.
 *
 * :copyright: Copyright 2007-2018 by the Sphinx team, see AUTHORS.
 * :license: BSD, see LICENSE for details.
 *
 */


/* Non-minified version JS is _stemmer.js if file is provided */ 
var JSX={};(function(h){function j(b,e){var a=function(){};a.prototype=e.prototype;var c=new a;for(var d in b){b[d].prototype=c}}function J(c,b){for(var a in b.prototype)if(b.prototype.hasOwnProperty(a))c.prototype[a]=b.prototype[a]}function f(a,b,d){function c(a,b,c){delete a[b];a[b]=c;return c}Object.defineProperty(a,b,{get:function(){return c(a,b,d())},set:function(d){c(a,b,d)},enumerable:true,configurable:true})}function K(a,b,c){return a[b]=a[b]/c|0}var p=parseInt;var z=parseFloat;function L(a){return a!==a}var x=isFinite;var w=encodeURIComponent;var u=decodeURIComponent;var t=encodeURI;var s=decodeURI;var B=Object.prototype.toString;var q=Object.prototype.hasOwnProperty;function i(){}h.require=function(b){var a=o[b];return a!==undefined?a:null};h.profilerIsRunning=function(){return i.getResults!=null};h.getProfileResults=function(){return(i.getResults||function(){return{}})()};h.postProfileResults=function(a,b){if(i.postResults==null)throw new Error('profiler has not been turned on');return i.postResults(a,b)};h.resetProfileResults=function(){if(i.resetResults==null)throw new Error('profiler has not been turned on');return i.resetResults()};h.DEBUG=false;function r(){};j([r],Error);function a(a,b,c){this.G=a.length;this.X=a;this.a=b;this.J=c;this.I=null;this.b=null};j([a],Object);function m(){};j([m],Object);function g(){var a;var b;var c;this.F={};a=this.D='';b=this._=0;c=this.A=a.length;this.E=0;this.B=b;this.C=c};j([g],m);function v(a,b){a.D=b.D;a._=b._;a.A=b.A;a.E=b.E;a.B=b.B;a.C=b.C};function k(b,d,c,e){var a;if(b._>=b.A){return false}a=b.D.charCodeAt(b._);if(a>e||a<c){return false}a-=c;if((d[a>>>3]&1<<(a&7))===0){return false}b._++;return true};function l(a,d,c,e){var b;if(a._>=a.A){return false}b=a.D.charCodeAt(a._);if(b>e||b<c){a._++;return true}b-=c;if((d[b>>>3]&1<<(b&7))===0){a._++;return true}return false};function d(a,b,d){var c;if(a._-a.E<b){return false}if(a.D.slice((c=a._)-b,c)!==d){return false}a._-=b;return true};function e(d,m,p){var b;var g;var e;var n;var f;var k;var l;var i;var h;var c;var a;var j;var o;b=0;g=p;e=d._;n=d.E;f=0;k=0;l=false;while(true){i=b+(g-b>>1);h=0;c=f<k?f:k;a=m[i];for(j=a.G-1-c;j>=0;j--){if(e-c===n){h=-1;break}h=d.D.charCodeAt(e-1-c)-a.X.charCodeAt(j);if(h!==0){break}c++}if(h<0){g=i;k=c}else{b=i;f=c}if(g-b<=1){if(b>0){break}if(g===b){break}if(l){break}l=true}}while(true){a=m[b];if(f>=a.G){d._=e-a.G|0;if(a.I==null){return a.J}o=a.I(d);d._=e-a.G|0;if(o){return a.J}}b=a.a;if(b<0){return 0}}return-1};function A(a,b,d,e){var c;c=e.length-(d-b);a.D=a.D.slice(0,b)+e+a.D.slice(d);a.A+=c|0;if(a._>=d){a._+=c|0}else if(a._>b){a._=b}return c|0};function c(a,f){var b;var c;var d;var e;b=false;if((c=a.B)<0||c>(d=a.C)||d>(e=a.A)||e>a.D.length?false:true){A(a,a.B,a.C,f);b=true}return b};g.prototype.H=function(){return false};g.prototype.Y=function(b){var a;var c;var d;var e;a=this.F['.'+b];if(a==null){c=this.D=b;d=this._=0;e=this.A=c.length;this.E=0;this.B=d;this.C=e;this.H();a=this.D;this.F['.'+b]=a}return a};g.prototype.stemWord=g.prototype.Y;g.prototype.Z=function(e){var d;var b;var c;var a;var f;var g;var h;d=[];for(b=0;b<e.length;b++){c=e[b];a=this.F['.'+c];if(a==null){f=this.D=c;g=this._=0;h=this.A=f.length;this.E=0;this.B=g;this.C=h;this.H();a=this.D;this.F['.'+c]=a}d.push(a)}return d};g.prototype.stemWords=g.prototype.Z;function b(){g.call(this);this.I_p2=0;this.I_pV=0};j([b],g);b.prototype.K=function(a){this.I_p2=a.I_p2;this.I_pV=a.I_pV;v(this,a)};b.prototype.copy_from=b.prototype.K;b.prototype.R=function(){var g;var a;var c;var d;var e;var f;var h;this.I_pV=h=this.A;this.I_p2=h;g=this._;a=true;a:while(a===true){a=false;b:while(true){c=true;c:while(c===true){c=false;if(!k(this,b.g_v,1072,1103)){break c}break b}if(this._>=this.A){break a}this._++}this.I_pV=this._;b:while(true){d=true;c:while(d===true){d=false;if(!l(this,b.g_v,1072,1103)){break c}break b}if(this._>=this.A){break a}this._++}b:while(true){e=true;c:while(e===true){e=false;if(!k(this,b.g_v,1072,1103)){break c}break b}if(this._>=this.A){break a}this._++}b:while(true){f=true;c:while(f===true){f=false;if(!l(this,b.g_v,1072,1103)){break c}break b}if(this._>=this.A){break a}this._++}this.I_p2=this._}this._=g;return true};b.prototype.r_mark_regions=b.prototype.R;function D(a){var h;var c;var d;var e;var f;var g;var i;a.I_pV=i=a.A;a.I_p2=i;h=a._;c=true;a:while(c===true){c=false;b:while(true){d=true;c:while(d===true){d=false;if(!k(a,b.g_v,1072,1103)){break c}break b}if(a._>=a.A){break a}a._++}a.I_pV=a._;b:while(true){e=true;c:while(e===true){e=false;if(!l(a,b.g_v,1072,1103)){break c}break b}if(a._>=a.A){break a}a._++}b:while(true){f=true;c:while(f===true){f=false;if(!k(a,b.g_v,1072,1103)){break c}break b}if(a._>=a.A){break a}a._++}b:while(true){g=true;c:while(g===true){g=false;if(!l(a,b.g_v,1072,1103)){break c}break b}if(a._>=a.A){break a}a._++}a.I_p2=a._}a._=h;return true};b.prototype.N=function(){return!(this.I_p2<=this._)?false:true};b.prototype.r_R2=b.prototype.N;b.prototype.T=function(){var a;var h;var f;var g;this.C=this._;a=e(this,b.a_0,9);if(a===0){return false}this.B=this._;switch(a){case 0:return false;case 1:f=true;a:while(f===true){f=false;h=this.A-this._;g=true;b:while(g===true){g=false;if(!d(this,1,'а')){break b}break a}this._=this.A-h;if(!d(this,1,'я')){return false}}if(!c(this,'')){return false}break;case 2:if(!c(this,'')){return false}break}return true};b.prototype.r_perfective_gerund=b.prototype.T;function E(a){var f;var i;var g;var h;a.C=a._;f=e(a,b.a_0,9);if(f===0){return false}a.B=a._;switch(f){case 0:return false;case 1:g=true;a:while(g===true){g=false;i=a.A-a._;h=true;b:while(h===true){h=false;if(!d(a,1,'а')){break b}break a}a._=a.A-i;if(!d(a,1,'я')){return false}}if(!c(a,'')){return false}break;case 2:if(!c(a,'')){return false}break}return true};b.prototype.P=function(){var a;this.C=this._;a=e(this,b.a_1,26);if(a===0){return false}this.B=this._;switch(a){case 0:return false;case 1:if(!c(this,'')){return false}break}return true};b.prototype.r_adjective=b.prototype.P;function n(a){var d;a.C=a._;d=e(a,b.a_1,26);if(d===0){return false}a.B=a._;switch(d){case 0:return false;case 1:if(!c(a,'')){return false}break}return true};b.prototype.O=function(){var f;var a;var j;var g;var h;var i;if(!n(this)){return false}a=this.A-this._;g=true;a:while(g===true){g=false;this.C=this._;f=e(this,b.a_2,8);if(f===0){this._=this.A-a;break a}this.B=this._;switch(f){case 0:this._=this.A-a;break a;case 1:h=true;b:while(h===true){h=false;j=this.A-this._;i=true;c:while(i===true){i=false;if(!d(this,1,'а')){break c}break b}this._=this.A-j;if(!d(this,1,'я')){this._=this.A-a;break a}}if(!c(this,'')){return false}break;case 2:if(!c(this,'')){return false}break}}return true};b.prototype.r_adjectival=b.prototype.O;function G(a){var g;var f;var k;var h;var i;var j;if(!n(a)){return false}f=a.A-a._;h=true;a:while(h===true){h=false;a.C=a._;g=e(a,b.a_2,8);if(g===0){a._=a.A-f;break a}a.B=a._;switch(g){case 0:a._=a.A-f;break a;case 1:i=true;b:while(i===true){i=false;k=a.A-a._;j=true;c:while(j===true){j=false;if(!d(a,1,'а')){break c}break b}a._=a.A-k;if(!d(a,1,'я')){a._=a.A-f;break a}}if(!c(a,'')){return false}break;case 2:if(!c(a,'')){return false}break}}return true};b.prototype.U=function(){var a;this.C=this._;a=e(this,b.a_3,2);if(a===0){return false}this.B=this._;switch(a){case 0:return false;case 1:if(!c(this,'')){return false}break}return true};b.prototype.r_reflexive=b.prototype.U;function H(a){var d;a.C=a._;d=e(a,b.a_3,2);if(d===0){return false}a.B=a._;switch(d){case 0:return false;case 1:if(!c(a,'')){return false}break}return true};b.prototype.W=function(){var a;var h;var f;var g;this.C=this._;a=e(this,b.a_4,46);if(a===0){return false}this.B=this._;switch(a){case 0:return false;case 1:f=true;a:while(f===true){f=false;h=this.A-this._;g=true;b:while(g===true){g=false;if(!d(this,1,'а')){break b}break a}this._=this.A-h;if(!d(this,1,'я')){return false}}if(!c(this,'')){return false}break;case 2:if(!c(this,'')){return false}break}return true};b.prototype.r_verb=b.prototype.W;function I(a){var f;var i;var g;var h;a.C=a._;f=e(a,b.a_4,46);if(f===0){return false}a.B=a._;switch(f){case 0:return false;case 1:g=true;a:while(g===true){g=false;i=a.A-a._;h=true;b:while(h===true){h=false;if(!d(a,1,'а')){break b}break a}a._=a.A-i;if(!d(a,1,'я')){return false}}if(!c(a,'')){return false}break;case 2:if(!c(a,'')){return false}break}return true};b.prototype.S=function(){var a;this.C=this._;a=e(this,b.a_5,36);if(a===0){return false}this.B=this._;switch(a){case 0:return false;case 1:if(!c(this,'')){return false}break}return true};b.prototype.r_noun=b.prototype.S;function F(a){var d;a.C=a._;d=e(a,b.a_5,36);if(d===0){return false}a.B=a._;switch(d){case 0:return false;case 1:if(!c(a,'')){return false}break}return true};b.prototype.Q=function(){var a;var d;this.C=this._;a=e(this,b.a_6,2);if(a===0){return false}this.B=d=this._;if(!(!(this.I_p2<=d)?false:true)){return false}switch(a){case 0:return false;case 1:if(!c(this,'')){return false}break}return true};b.prototype.r_derivational=b.prototype.Q;function C(a){var d;var f;a.C=a._;d=e(a,b.a_6,2);if(d===0){return false}a.B=f=a._;if(!(!(a.I_p2<=f)?false:true)){return false}switch(d){case 0:return false;case 1:if(!c(a,'')){return false}break}return true};b.prototype.V=function(){var a;this.C=this._;a=e(this,b.a_7,4);if(a===0){return false}this.B=this._;switch(a){case 0:return false;case 1:if(!c(this,'')){return false}this.C=this._;if(!d(this,1,'н')){return false}this.B=this._;if(!d(this,1,'н')){return false}if(!c(this,'')){return false}break;case 2:if(!d(this,1,'н')){return false}if(!c(this,'')){return false}break;case 3:if(!c(this,'')){return false}break}return true};b.prototype.r_tidy_up=b.prototype.V;function y(a){var f;a.C=a._;f=e(a,b.a_7,4);if(f===0){return false}a.B=a._;switch(f){case 0:return false;case 1:if(!c(a,'')){return false}a.C=a._;if(!d(a,1,'н')){return false}a.B=a._;if(!d(a,1,'н')){return false}if(!c(a,'')){return false}break;case 2:if(!d(a,1,'н')){return false}if(!c(a,'')){return false}break;case 3:if(!c(a,'')){return false}break}return true};b.prototype.H=function(){var s;var v;var w;var A;var p;var q;var i;var t;var u;var e;var f;var g;var h;var a;var j;var b;var k;var l;var m;var n;var x;var z;var o;var B;var J;var K;var L;var M;var N;var O;var r;s=this._;e=true;a:while(e===true){e=false;if(!D(this)){break a}}x=this._=s;this.E=x;o=this._=z=this.A;v=z-o;if(o<this.I_pV){return false}K=this._=this.I_pV;w=this.E;this.E=K;M=this._=(L=this.A)-v;A=L-M;f=true;c:while(f===true){f=false;g=true;b:while(g===true){g=false;p=this.A-this._;h=true;a:while(h===true){h=false;if(!E(this)){break a}break b}J=this._=(B=this.A)-p;q=B-J;a=true;a:while(a===true){a=false;if(!H(this)){this._=this.A-q;break a}}j=true;a:while(j===true){j=false;i=this.A-this._;b=true;d:while(b===true){b=false;if(!G(this)){break d}break a}this._=this.A-i;k=true;d:while(k===true){k=false;if(!I(this)){break d}break a}this._=this.A-i;if(!F(this)){break c}}}}O=this._=(N=this.A)-A;t=N-O;l=true;a:while(l===true){l=false;this.C=this._;if(!d(this,1,'и')){this._=this.A-t;break a}this.B=this._;if(!c(this,'')){return false}}u=this.A-this._;m=true;a:while(m===true){m=false;if(!C(this)){break a}}this._=this.A-u;n=true;a:while(n===true){n=false;if(!y(this)){break a}}r=this.E=w;this._=r;return true};b.prototype.stem=b.prototype.H;b.prototype.L=function(a){return a instanceof b};b.prototype.equals=b.prototype.L;b.prototype.M=function(){var c;var a;var b;var d;c='RussianStemmer';a=0;for(b=0;b<c.length;b++){d=c.charCodeAt(b);a=(a<<5)-a+d;a=a&a}return a|0};b.prototype.hashCode=b.prototype.M;b.serialVersionUID=1;f(b,'methodObject',function(){return new b});f(b,'a_0',function(){return[new a('в',-1,1),new a('ив',0,2),new a('ыв',0,2),new a('вши',-1,1),new a('ивши',3,2),new a('ывши',3,2),new a('вшись',-1,1),new a('ившись',6,2),new a('ывшись',6,2)]});f(b,'a_1',function(){return[new a('ее',-1,1),new a('ие',-1,1),new a('ое',-1,1),new a('ые',-1,1),new a('ими',-1,1),new a('ыми',-1,1),new a('ей',-1,1),new a('ий',-1,1),new a('ой',-1,1),new a('ый',-1,1),new a('ем',-1,1),new a('им',-1,1),new a('ом',-1,1),new a('ым',-1,1),new a('его',-1,1),new a('ого',-1,1),new a('ему',-1,1),new a('ому',-1,1),new a('их',-1,1),new a('ых',-1,1),new a('ею',-1,1),new a('ою',-1,1),new a('ую',-1,1),new a('юю',-1,1),new a('ая',-1,1),new a('яя',-1,1)]});f(b,'a_2',function(){return[new a('ем',-1,1),new a('нн',-1,1),new a('вш',-1,1),new a('ивш',2,2),new a('ывш',2,2),new a('щ',-1,1),new a('ющ',5,1),new a('ующ',6,2)]});f(b,'a_3',function(){return[new a('сь',-1,1),new a('ся',-1,1)]});f(b,'a_4',function(){return[new a('ла',-1,1),new a('ила',0,2),new a('ыла',0,2),new a('на',-1,1),new a('ена',3,2),new a('ете',-1,1),new a('ите',-1,2),new a('йте',-1,1),new a('ейте',7,2),new a('уйте',7,2),new a('ли',-1,1),new a('или',10,2),new a('ыли',10,2),new a('й',-1,1),new a('ей',13,2),new a('уй',13,2),new a('л',-1,1),new a('ил',16,2),new a('ыл',16,2),new a('ем',-1,1),new a('им',-1,2),new a('ым',-1,2),new a('н',-1,1),new a('ен',22,2),new a('ло',-1,1),new a('ило',24,2),new a('ыло',24,2),new a('но',-1,1),new a('ено',27,2),new a('нно',27,1),new a('ет',-1,1),new a('ует',30,2),new a('ит',-1,2),new a('ыт',-1,2),new a('ют',-1,1),new a('уют',34,2),new a('ят',-1,2),new a('ны',-1,1),new a('ены',37,2),new a('ть',-1,1),new a('ить',39,2),new a('ыть',39,2),new a('ешь',-1,1),new a('ишь',-1,2),new a('ю',-1,2),new a('ую',44,2)]});f(b,'a_5',function(){return[new a('а',-1,1),new a('ев',-1,1),new a('ов',-1,1),new a('е',-1,1),new a('ие',3,1),new a('ье',3,1),new a('и',-1,1),new a('еи',6,1),new a('ии',6,1),new a('ами',6,1),new a('ями',6,1),new a('иями',10,1),new a('й',-1,1),new a('ей',12,1),new a('ией',13,1),new a('ий',12,1),new a('ой',12,1),new a('ам',-1,1),new a('ем',-1,1),new a('ием',18,1),new a('ом',-1,1),new a('ям',-1,1),new a('иям',21,1),new a('о',-1,1),new a('у',-1,1),new a('ах',-1,1),new a('ях',-1,1),new a('иях',26,1),new a('ы',-1,1),new a('ь',-1,1),new a('ю',-1,1),new a('ию',30,1),new a('ью',30,1),new a('я',-1,1),new a('ия',33,1),new a('ья',33,1)]});f(b,'a_6',function(){return[new a('ост',-1,1),new a('ость',-1,1)]});f(b,'a_7',function(){return[new a('ейше',-1,1),new a('н',-1,2),new a('ейш',-1,1),new a('ь',-1,3)]});f(b,'g_v',function(){return[33,65,8,232]});var o={'src/stemmer.jsx':{Stemmer:m},'src/russian-stemmer.jsx':{RussianStemmer:b}}}(JSX))
var Stemmer = JSX.require("src/russian-stemmer.jsx").RussianStemmer;



/**
 * Simple result scoring code.
 */
var Scorer = {
  // Implement the following function to further tweak the score for each result
  // The function takes a result array [filename, title, anchor, descr, score]
  // and returns the new score.
  /*
  score: function(result) {
    return result[4];
  },
  */

  // query matches the full name of an object
  objNameMatch: 11,
  // or matches in the last dotted part of the object name
  objPartialMatch: 6,
  // Additive scores depending on the priority of the object
  objPrio: {0:  15,   // used to be importantResults
            1:  5,   // used to be objectResults
            2: -5},  // used to be unimportantResults
  //  Used when the priority is not in the mapping.
  objPrioDefault: 0,

  // query found in title
  title: 15,
  // query found in terms
  term: 5
};





var splitChars = (function() {
    var result = {};
    var singles = [96, 180, 187, 191, 215, 247, 749, 885, 903, 907, 909, 930, 1014, 1648,
         1748, 1809, 2416, 2473, 2481, 2526, 2601, 2609, 2612, 2615, 2653, 2702,
         2706, 2729, 2737, 2740, 2857, 2865, 2868, 2910, 2928, 2948, 2961, 2971,
         2973, 3085, 3089, 3113, 3124, 3213, 3217, 3241, 3252, 3295, 3341, 3345,
         3369, 3506, 3516, 3633, 3715, 3721, 3736, 3744, 3748, 3750, 3756, 3761,
         3781, 3912, 4239, 4347, 4681, 4695, 4697, 4745, 4785, 4799, 4801, 4823,
         4881, 5760, 5901, 5997, 6313, 7405, 8024, 8026, 8028, 8030, 8117, 8125,
         8133, 8181, 8468, 8485, 8487, 8489, 8494, 8527, 11311, 11359, 11687, 11695,
         11703, 11711, 11719, 11727, 11735, 12448, 12539, 43010, 43014, 43019, 43587,
         43696, 43713, 64286, 64297, 64311, 64317, 64319, 64322, 64325, 65141];
    var i, j, start, end;
    for (i = 0; i < singles.length; i++) {
        result[singles[i]] = true;
    }
    var ranges = [[0, 47], [58, 64], [91, 94], [123, 169], [171, 177], [182, 184], [706, 709],
         [722, 735], [741, 747], [751, 879], [888, 889], [894, 901], [1154, 1161],
         [1318, 1328], [1367, 1368], [1370, 1376], [1416, 1487], [1515, 1519], [1523, 1568],
         [1611, 1631], [1642, 1645], [1750, 1764], [1767, 1773], [1789, 1790], [1792, 1807],
         [1840, 1868], [1958, 1968], [1970, 1983], [2027, 2035], [2038, 2041], [2043, 2047],
         [2070, 2073], [2075, 2083], [2085, 2087], [2089, 2307], [2362, 2364], [2366, 2383],
         [2385, 2391], [2402, 2405], [2419, 2424], [2432, 2436], [2445, 2446], [2449, 2450],
         [2483, 2485], [2490, 2492], [2494, 2509], [2511, 2523], [2530, 2533], [2546, 2547],
         [2554, 2564], [2571, 2574], [2577, 2578], [2618, 2648], [2655, 2661], [2672, 2673],
         [2677, 2692], [2746, 2748], [2750, 2767], [2769, 2783], [2786, 2789], [2800, 2820],
         [2829, 2830], [2833, 2834], [2874, 2876], [2878, 2907], [2914, 2917], [2930, 2946],
         [2955, 2957], [2966, 2968], [2976, 2978], [2981, 2983], [2987, 2989], [3002, 3023],
         [3025, 3045], [3059, 3076], [3130, 3132], [3134, 3159], [3162, 3167], [3170, 3173],
         [3184, 3191], [3199, 3204], [3258, 3260], [3262, 3293], [3298, 3301], [3312, 3332],
         [3386, 3388], [3390, 3423], [3426, 3429], [3446, 3449], [3456, 3460], [3479, 3481],
         [3518, 3519], [3527, 3584], [3636, 3647], [3655, 3663], [3674, 3712], [3717, 3718],
         [3723, 3724], [3726, 3731], [3752, 3753], [3764, 3772], [3774, 3775], [3783, 3791],
         [3802, 3803], [3806, 3839], [3841, 3871], [3892, 3903], [3949, 3975], [3980, 4095],
         [4139, 4158], [4170, 4175], [4182, 4185], [4190, 4192], [4194, 4196], [4199, 4205],
         [4209, 4212], [4226, 4237], [4250, 4255], [4294, 4303], [4349, 4351], [4686, 4687],
         [4702, 4703], [4750, 4751], [4790, 4791], [4806, 4807], [4886, 4887], [4955, 4968],
         [4989, 4991], [5008, 5023], [5109, 5120], [5741, 5742], [5787, 5791], [5867, 5869],
         [5873, 5887], [5906, 5919], [5938, 5951], [5970, 5983], [6001, 6015], [6068, 6102],
         [6104, 6107], [6109, 6111], [6122, 6127], [6138, 6159], [6170, 6175], [6264, 6271],
         [6315, 6319], [6390, 6399], [6429, 6469], [6510, 6511], [6517, 6527], [6572, 6592],
         [6600, 6607], [6619, 6655], [6679, 6687], [6741, 6783], [6794, 6799], [6810, 6822],
         [6824, 6916], [6964, 6980], [6988, 6991], [7002, 7042], [7073, 7085], [7098, 7167],
         [7204, 7231], [7242, 7244], [7294, 7400], [7410, 7423], [7616, 7679], [7958, 7959],
         [7966, 7967], [8006, 8007], [8014, 8015], [8062, 8063], [8127, 8129], [8141, 8143],
         [8148, 8149], [8156, 8159], [8173, 8177], [8189, 8303], [8306, 8307], [8314, 8318],
         [8330, 8335], [8341, 8449], [8451, 8454], [8456, 8457], [8470, 8472], [8478, 8483],
         [8506, 8507], [8512, 8516], [8522, 8525], [8586, 9311], [9372, 9449], [9472, 10101],
         [10132, 11263], [11493, 11498], [11503, 11516], [11518, 11519], [11558, 11567],
         [11622, 11630], [11632, 11647], [11671, 11679], [11743, 11822], [11824, 12292],
         [12296, 12320], [12330, 12336], [12342, 12343], [12349, 12352], [12439, 12444],
         [12544, 12548], [12590, 12592], [12687, 12689], [12694, 12703], [12728, 12783],
         [12800, 12831], [12842, 12880], [12896, 12927], [12938, 12976], [12992, 13311],
         [19894, 19967], [40908, 40959], [42125, 42191], [42238, 42239], [42509, 42511],
         [42540, 42559], [42592, 42593], [42607, 42622], [42648, 42655], [42736, 42774],
         [42784, 42785], [42889, 42890], [42893, 43002], [43043, 43055], [43062, 43071],
         [43124, 43137], [43188, 43215], [43226, 43249], [43256, 43258], [43260, 43263],
         [43302, 43311], [43335, 43359], [43389, 43395], [43443, 43470], [43482, 43519],
         [43561, 43583], [43596, 43599], [43610, 43615], [43639, 43641], [43643, 43647],
         [43698, 43700], [43703, 43704], [43710, 43711], [43715, 43738], [43742, 43967],
         [44003, 44015], [44026, 44031], [55204, 55215], [55239, 55242], [55292, 55295],
         [57344, 63743], [64046, 64047], [64110, 64111], [64218, 64255], [64263, 64274],
         [64280, 64284], [64434, 64466], [64830, 64847], [64912, 64913], [64968, 65007],
         [65020, 65135], [65277, 65295], [65306, 65312], [65339, 65344], [65371, 65381],
         [65471, 65473], [65480, 65481], [65488, 65489], [65496, 65497]];
    for (i = 0; i < ranges.length; i++) {
        start = ranges[i][0];
        end = ranges[i][1];
        for (j = start; j <= end; j++) {
            result[j] = true;
        }
    }
    return result;
})();

function splitQuery(query) {
    var result = [];
    var start = -1;
    for (var i = 0; i < query.length; i++) {
        if (splitChars[query.charCodeAt(i)]) {
            if (start !== -1) {
                result.push(query.slice(start, i));
                start = -1;
            }
        } else if (start === -1) {
            start = i;
        }
    }
    if (start !== -1) {
        result.push(query.slice(start));
    }
    return result;
}




/**
 * Search Module
 */
var Search = {

  _index : null,
  _queued_query : null,
  _pulse_status : -1,

  init : function() {
      var params = $.getQueryParameters();
      if (params.q) {
          var query = params.q[0];
          $('input[name="q"]')[0].value = query;
          this.performSearch(query);
      }
  },

  loadIndex : function(url) {
    $.ajax({type: "GET", url: url, data: null,
            dataType: "script", cache: true,
            complete: function(jqxhr, textstatus) {
              if (textstatus != "success") {
                document.getElementById("searchindexloader").src = url;
              }
            }});
  },

  setIndex : function(index) {
    var q;
    this._index = index;
    if ((q = this._queued_query) !== null) {
      this._queued_query = null;
      Search.query(q);
    }
  },

  hasIndex : function() {
      return this._index !== null;
  },

  deferQuery : function(query) {
      this._queued_query = query;
  },

  stopPulse : function() {
      this._pulse_status = 0;
  },

  startPulse : function() {
    if (this._pulse_status >= 0)
        return;
    function pulse() {
      var i;
      Search._pulse_status = (Search._pulse_status + 1) % 4;
      var dotString = '';
      for (i = 0; i < Search._pulse_status; i++)
        dotString += '.';
      Search.dots.text(dotString);
      if (Search._pulse_status > -1)
        window.setTimeout(pulse, 500);
    }
    pulse();
  },

  /**
   * perform a search for something (or wait until index is loaded)
   */
  performSearch : function(query) {
    // create the required interface elements
    this.out = $('#search-results');
    this.title = $('<h2>' + _('Searching') + '</h2>').appendTo(this.out);
    this.dots = $('<span></span>').appendTo(this.title);
    this.status = $('<p style="display: none"></p>').appendTo(this.out);
    this.output = $('<ul class="search"/>').appendTo(this.out);

    $('#search-progress').text(_('Preparing search...'));
    this.startPulse();

    // index already loaded, the browser was quick!
    if (this.hasIndex())
      this.query(query);
    else
      this.deferQuery(query);
  },

  /**
   * execute search (requires search index to be loaded)
   */
  query : function(query) {
    var i;
    var stopwords = ["\u0430","\u0431\u0435\u0437","\u0431\u043e\u043b\u0435\u0435","\u0431\u043e\u043b\u044c\u0448\u0435","\u0431\u0443\u0434\u0435\u0442","\u0431\u0443\u0434\u0442\u043e","\u0431\u044b","\u0431\u044b\u043b","\u0431\u044b\u043b\u0430","\u0431\u044b\u043b\u0438","\u0431\u044b\u043b\u043e","\u0431\u044b\u0442\u044c","\u0432","\u0432\u0430\u043c","\u0432\u0430\u0441","\u0432\u0434\u0440\u0443\u0433","\u0432\u0435\u0434\u044c","\u0432\u043e","\u0432\u043e\u0442","\u0432\u043f\u0440\u043e\u0447\u0435\u043c","\u0432\u0441\u0435","\u0432\u0441\u0435\u0433\u0434\u0430","\u0432\u0441\u0435\u0433\u043e","\u0432\u0441\u0435\u0445","\u0432\u0441\u044e","\u0432\u044b","\u0433\u0434\u0435","\u0433\u043e\u0432\u043e\u0440\u0438\u043b","\u0434\u0430","\u0434\u0430\u0436\u0435","\u0434\u0432\u0430","\u0434\u043b\u044f","\u0434\u043e","\u0434\u0440\u0443\u0433\u043e\u0439","\u0435\u0433\u043e","\u0435\u0435","\u0435\u0439","\u0435\u043c\u0443","\u0435\u0441\u043b\u0438","\u0435\u0441\u0442\u044c","\u0435\u0449\u0435","\u0436","\u0436\u0435","\u0436\u0438\u0437\u043d\u044c","\u0437\u0430","\u0437\u0430\u0447\u0435\u043c","\u0437\u0434\u0435\u0441\u044c","\u0438","\u0438\u0437","\u0438\u043b\u0438","\u0438\u043c","\u0438\u043d\u043e\u0433\u0434\u0430","\u0438\u0445","\u043a","\u043a\u0430\u0436\u0435\u0442\u0441\u044f","\u043a\u0430\u043a","\u043a\u0430\u043a\u0430\u044f","\u043a\u0430\u043a\u043e\u0439","\u043a\u043e\u0433\u0434\u0430","\u043a\u043e\u043d\u0435\u0447\u043d\u043e","\u043a\u0442\u043e","\u043a\u0443\u0434\u0430","\u043b\u0438","\u043b\u0443\u0447\u0448\u0435","\u043c\u0435\u0436\u0434\u0443","\u043c\u0435\u043d\u044f","\u043c\u043d\u0435","\u043c\u043d\u043e\u0433\u043e","\u043c\u043e\u0436\u0435\u0442","\u043c\u043e\u0436\u043d\u043e","\u043c\u043e\u0439","\u043c\u043e\u044f","\u043c\u044b","\u043d\u0430","\u043d\u0430\u0434","\u043d\u0430\u0434\u043e","\u043d\u0430\u043a\u043e\u043d\u0435\u0446","\u043d\u0430\u0441","\u043d\u0435","\u043d\u0435\u0433\u043e","\u043d\u0435\u0435","\u043d\u0435\u0439","\u043d\u0435\u043b\u044c\u0437\u044f","\u043d\u0435\u0442","\u043d\u0438","\u043d\u0438\u0431\u0443\u0434\u044c","\u043d\u0438\u043a\u043e\u0433\u0434\u0430","\u043d\u0438\u043c","\u043d\u0438\u0445","\u043d\u0438\u0447\u0435\u0433\u043e","\u043d\u043e","\u043d\u0443","\u043e","\u043e\u0431","\u043e\u0434\u0438\u043d","\u043e\u043d","\u043e\u043d\u0430","\u043e\u043d\u0438","\u043e\u043f\u044f\u0442\u044c","\u043e\u0442","\u043f\u0435\u0440\u0435\u0434","\u043f\u043e","\u043f\u043e\u0434","\u043f\u043e\u0441\u043b\u0435","\u043f\u043e\u0442\u043e\u043c","\u043f\u043e\u0442\u043e\u043c\u0443","\u043f\u043e\u0447\u0442\u0438","\u043f\u0440\u0438","\u043f\u0440\u043e","\u0440\u0430\u0437","\u0440\u0430\u0437\u0432\u0435","\u0441","\u0441\u0430\u043c","\u0441\u0432\u043e\u044e","\u0441\u0435\u0431\u0435","\u0441\u0435\u0431\u044f","\u0441\u0435\u0433\u043e\u0434\u043d\u044f","\u0441\u0435\u0439\u0447\u0430\u0441","\u0441\u043a\u0430\u0437\u0430\u043b","\u0441\u043a\u0430\u0437\u0430\u043b\u0430","\u0441\u043a\u0430\u0437\u0430\u0442\u044c","\u0441\u043e","\u0441\u043e\u0432\u0441\u0435\u043c","\u0442\u0430\u043a","\u0442\u0430\u043a\u043e\u0439","\u0442\u0430\u043c","\u0442\u0435\u0431\u044f","\u0442\u0435\u043c","\u0442\u0435\u043f\u0435\u0440\u044c","\u0442\u043e","\u0442\u043e\u0433\u0434\u0430","\u0442\u043e\u0433\u043e","\u0442\u043e\u0436\u0435","\u0442\u043e\u043b\u044c\u043a\u043e","\u0442\u043e\u043c","\u0442\u043e\u0442","\u0442\u0440\u0438","\u0442\u0443\u0442","\u0442\u044b","\u0443","\u0443\u0436","\u0443\u0436\u0435","\u0445\u043e\u0440\u043e\u0448\u043e","\u0445\u043e\u0442\u044c","\u0447\u0435\u0433\u043e","\u0447\u0435\u043b\u043e\u0432\u0435\u043a","\u0447\u0435\u043c","\u0447\u0435\u0440\u0435\u0437","\u0447\u0442\u043e","\u0447\u0442\u043e\u0431","\u0447\u0442\u043e\u0431\u044b","\u0447\u0443\u0442\u044c","\u044d\u0442\u0438","\u044d\u0442\u043e\u0433\u043e","\u044d\u0442\u043e\u0439","\u044d\u0442\u043e\u043c","\u044d\u0442\u043e\u0442","\u044d\u0442\u0443","\u044f"];

    // stem the searchterms and add them to the correct list
    var stemmer = new Stemmer();
    var searchterms = [];
    var excluded = [];
    var hlterms = [];
    var tmp = splitQuery(query);
    var objectterms = [];
    for (i = 0; i < tmp.length; i++) {
      if (tmp[i] !== "") {
          objectterms.push(tmp[i].toLowerCase());
      }

      if ($u.indexOf(stopwords, tmp[i].toLowerCase()) != -1 || tmp[i].match(/^\d+$/) ||
          tmp[i] === "") {
        // skip this "word"
        continue;
      }
      // stem the word
      var word = stemmer.stemWord(tmp[i].toLowerCase());
      // prevent stemmer from cutting word smaller than two chars
      if(word.length < 3 && tmp[i].length >= 3) {
        word = tmp[i];
      }
      var toAppend;
      // select the correct list
      if (word[0] == '-') {
        toAppend = excluded;
        word = word.substr(1);
      }
      else {
        toAppend = searchterms;
        hlterms.push(tmp[i].toLowerCase());
      }
      // only add if not already in the list
      if (!$u.contains(toAppend, word))
        toAppend.push(word);
    }
    var highlightstring = '?highlight=' + $.urlencode(hlterms.join(" "));

    // console.debug('SEARCH: searching for:');
    // console.info('required: ', searchterms);
    // console.info('excluded: ', excluded);

    // prepare search
    var terms = this._index.terms;
    var titleterms = this._index.titleterms;

    // array of [filename, title, anchor, descr, score]
    var results = [];
    $('#search-progress').empty();

    // lookup as object
    for (i = 0; i < objectterms.length; i++) {
      var others = [].concat(objectterms.slice(0, i),
                             objectterms.slice(i+1, objectterms.length));
      results = results.concat(this.performObjectSearch(objectterms[i], others));
    }

    // lookup as search terms in fulltext
    results = results.concat(this.performTermsSearch(searchterms, excluded, terms, titleterms));

    // let the scorer override scores with a custom scoring function
    if (Scorer.score) {
      for (i = 0; i < results.length; i++)
        results[i][4] = Scorer.score(results[i]);
    }

    // now sort the results by score (in opposite order of appearance, since the
    // display function below uses pop() to retrieve items) and then
    // alphabetically
    results.sort(function(a, b) {
      var left = a[4];
      var right = b[4];
      if (left > right) {
        return 1;
      } else if (left < right) {
        return -1;
      } else {
        // same score: sort alphabetically
        left = a[1].toLowerCase();
        right = b[1].toLowerCase();
        return (left > right) ? -1 : ((left < right) ? 1 : 0);
      }
    });

    // for debugging
    //Search.lastresults = results.slice();  // a copy
    //console.info('search results:', Search.lastresults);

    // print the results
    var resultCount = results.length;
    function displayNextItem() {
      // results left, load the summary and display it
      if (results.length) {
        var item = results.pop();
        var listItem = $('<li style="display:none"></li>');
        if (DOCUMENTATION_OPTIONS.FILE_SUFFIX === '') {
          // dirhtml builder
          var dirname = item[0] + '/';
          if (dirname.match(/\/index\/$/)) {
            dirname = dirname.substring(0, dirname.length-6);
          } else if (dirname == 'index/') {
            dirname = '';
          }
          listItem.append($('<a/>').attr('href',
            DOCUMENTATION_OPTIONS.URL_ROOT + dirname +
            highlightstring + item[2]).html(item[1]));
        } else {
          // normal html builders
          listItem.append($('<a/>').attr('href',
            item[0] + DOCUMENTATION_OPTIONS.FILE_SUFFIX +
            highlightstring + item[2]).html(item[1]));
        }
        if (item[3]) {
          listItem.append($('<span> (' + item[3] + ')</span>'));
          Search.output.append(listItem);
          listItem.slideDown(5, function() {
            displayNextItem();
          });
        } else if (DOCUMENTATION_OPTIONS.HAS_SOURCE) {
          var suffix = DOCUMENTATION_OPTIONS.SOURCELINK_SUFFIX;
          if (suffix === undefined) {
            suffix = '.txt';
          }
          $.ajax({url: DOCUMENTATION_OPTIONS.URL_ROOT + '_sources/' + item[5] + (item[5].slice(-suffix.length) === suffix ? '' : suffix),
                  dataType: "text",
                  complete: function(jqxhr, textstatus) {
                    var data = jqxhr.responseText;
                    if (data !== '' && data !== undefined) {
                      listItem.append(Search.makeSearchSummary(data, searchterms, hlterms));
                    }
                    Search.output.append(listItem);
                    listItem.slideDown(5, function() {
                      displayNextItem();
                    });
                  }});
        } else {
          // no source available, just display title
          Search.output.append(listItem);
          listItem.slideDown(5, function() {
            displayNextItem();
          });
        }
      }
      // search finished, update title and status message
      else {
        Search.stopPulse();
        Search.title.text(_('Search Results'));
        if (!resultCount)
          Search.status.text(_('Your search did not match any documents. Please make sure that all words are spelled correctly and that you\'ve selected enough categories.'));
        else
            Search.status.text(_('Search finished, found %s page(s) matching the search query.').replace('%s', resultCount));
        Search.status.fadeIn(500);
      }
    }
    displayNextItem();
  },

  /**
   * search for object names
   */
  performObjectSearch : function(object, otherterms) {
    var filenames = this._index.filenames;
    var docnames = this._index.docnames;
    var objects = this._index.objects;
    var objnames = this._index.objnames;
    var titles = this._index.titles;

    var i;
    var results = [];

    for (var prefix in objects) {
      for (var name in objects[prefix]) {
        var fullname = (prefix ? prefix + '.' : '') + name;
        if (fullname.toLowerCase().indexOf(object) > -1) {
          var score = 0;
          var parts = fullname.split('.');
          // check for different match types: exact matches of full name or
          // "last name" (i.e. last dotted part)
          if (fullname == object || parts[parts.length - 1] == object) {
            score += Scorer.objNameMatch;
          // matches in last name
          } else if (parts[parts.length - 1].indexOf(object) > -1) {
            score += Scorer.objPartialMatch;
          }
          var match = objects[prefix][name];
          var objname = objnames[match[1]][2];
          var title = titles[match[0]];
          // If more than one term searched for, we require other words to be
          // found in the name/title/description
          if (otherterms.length > 0) {
            var haystack = (prefix + ' ' + name + ' ' +
                            objname + ' ' + title).toLowerCase();
            var allfound = true;
            for (i = 0; i < otherterms.length; i++) {
              if (haystack.indexOf(otherterms[i]) == -1) {
                allfound = false;
                break;
              }
            }
            if (!allfound) {
              continue;
            }
          }
          var descr = objname + _(', in ') + title;

          var anchor = match[3];
          if (anchor === '')
            anchor = fullname;
          else if (anchor == '-')
            anchor = objnames[match[1]][1] + '-' + fullname;
          // add custom score for some objects according to scorer
          if (Scorer.objPrio.hasOwnProperty(match[2])) {
            score += Scorer.objPrio[match[2]];
          } else {
            score += Scorer.objPrioDefault;
          }
          results.push([docnames[match[0]], fullname, '#'+anchor, descr, score, filenames[match[0]]]);
        }
      }
    }

    return results;
  },

  /**
   * search for full-text terms in the index
   */
  performTermsSearch : function(searchterms, excluded, terms, titleterms) {
    var docnames = this._index.docnames;
    var filenames = this._index.filenames;
    var titles = this._index.titles;

    var i, j, file;
    var fileMap = {};
    var scoreMap = {};
    var results = [];

    // perform the search on the required terms
    for (i = 0; i < searchterms.length; i++) {
      var word = searchterms[i];
      var files = [];
      var _o = [
        {files: terms[word], score: Scorer.term},
        {files: titleterms[word], score: Scorer.title}
      ];

      // no match but word was a required one
      if ($u.every(_o, function(o){return o.files === undefined;})) {
        break;
      }
      // found search word in contents
      $u.each(_o, function(o) {
        var _files = o.files;
        if (_files === undefined)
          return

        if (_files.length === undefined)
          _files = [_files];
        files = files.concat(_files);

        // set score for the word in each file to Scorer.term
        for (j = 0; j < _files.length; j++) {
          file = _files[j];
          if (!(file in scoreMap))
            scoreMap[file] = {}
          scoreMap[file][word] = o.score;
        }
      });

      // create the mapping
      for (j = 0; j < files.length; j++) {
        file = files[j];
        if (file in fileMap)
          fileMap[file].push(word);
        else
          fileMap[file] = [word];
      }
    }

    // now check if the files don't contain excluded terms
    for (file in fileMap) {
      var valid = true;

      // check if all requirements are matched
      if (fileMap[file].length != searchterms.length)
          continue;

      // ensure that none of the excluded terms is in the search result
      for (i = 0; i < excluded.length; i++) {
        if (terms[excluded[i]] == file ||
            titleterms[excluded[i]] == file ||
            $u.contains(terms[excluded[i]] || [], file) ||
            $u.contains(titleterms[excluded[i]] || [], file)) {
          valid = false;
          break;
        }
      }

      // if we have still a valid result we can add it to the result list
      if (valid) {
        // select one (max) score for the file.
        // for better ranking, we should calculate ranking by using words statistics like basic tf-idf...
        var score = $u.max($u.map(fileMap[file], function(w){return scoreMap[file][w]}));
        results.push([docnames[file], titles[file], '', null, score, filenames[file]]);
      }
    }
    return results;
  },

  /**
   * helper function to return a node containing the
   * search summary for a given text. keywords is a list
   * of stemmed words, hlwords is the list of normal, unstemmed
   * words. the first one is used to find the occurrence, the
   * latter for highlighting it.
   */
  makeSearchSummary : function(text, keywords, hlwords) {
    var textLower = text.toLowerCase();
    var start = 0;
    $.each(keywords, function() {
      var i = textLower.indexOf(this.toLowerCase());
      if (i > -1)
        start = i;
    });
    start = Math.max(start - 120, 0);
    var excerpt = ((start > 0) ? '...' : '') +
      $.trim(text.substr(start, 240)) +
      ((start + 240 - text.length) ? '...' : '');
    var rv = $('<div class="context"></div>').text(excerpt);
    $.each(hlwords, function() {
      rv = rv.highlightText(this, 'highlighted');
    });
    return rv;
  }
};

$(document).ready(function() {
  Search.init();
});