import numpy as np, trimesh, math, os
from trimesh.transformations import rotation_matrix
S=trimesh.Scene(); materials={}
C={'white':[235,239,240,255],'cream':[217,225,229,255],'red':[164,37,46,255],'blue':[22,56,85,255],'dark':[30,38,44,255],'rubber':[20,22,24,255],'metal':[154,163,169,255],'glass':[80,142,168,160],'wood':[93,65,48,255],'instrument':[28,35,39,255],'light':[226,230,214,255],'seat':[59,70,79,255],'orange':[242,169,59,255]}
def add(name, mesh, color='white'):
 mesh.visual.vertex_colors=np.tile(C.get(color,color),(len(mesh.vertices),1)); S.add_geometry(mesh,geom_name=name,node_name=name);return mesh
def uvball(name,center,scale,color='white',sub=2):
 m=trimesh.creation.icosphere(subdivisions=sub,radius=1);m.apply_scale(scale);m.apply_translation(center);return add(name,m,color)
def box(name,center,ext,color='white'):
 m=trimesh.creation.box(extents=ext);m.apply_translation(center);return add(name,m,color)
def beam(name,p,q,r,color='metal',sections=12):
 a=np.array(p,float);b=np.array(q,float);d=b-a;l=np.linalg.norm(d);m=trimesh.creation.cylinder(radius=r,height=l,sections=sections);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],d));m.apply_translation((a+b)/2);return add(name,m,color)
def ring(name,c,axis,outer,inner,color='metal'):
 m=trimesh.creation.annulus(r_min=inner,r_max=outer,height=.018,sections=32);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],axis));m.apply_translation(c);return add(name,m,color)
def loft(name,stations,color='white',count=32):
 # stations list (x, yc, zc, horizontal-radius, vertical-radius)
 v=[]; f=[]
 for x,y,z,ry,rz in stations:
  for i in range(count):
   t=2*np.pi*i/count; v.append([x,y+ry*np.cos(t),z+rz*np.sin(t)])
 for j in range(len(stations)-1):
  for i in range(count):
   a=j*count+i; b=j*count+(i+1)%count;c=(j+1)*count+i; d=(j+1)*count+(i+1)%count
   f.extend([[a,b,c],[b,d,c]])
 f.extend([[0,i+1,i] for i in range(1,count-1)])
 k=(len(stations)-1)*count;f.extend([[k,k+i,k+i+1] for i in range(1,count-1)])
 return add(name,trimesh.Trimesh(vertices=v,faces=f,process=False),color)
def wingmesh(name, strips, color='white', naca=.12):
 # strips: tuples(y, x-front, x-back, z, dihedral)
 V=[];F=[]; N=15
 for y,xf,xb,z,_ in strips:
  chord=xb-xf
  for side in [1,-1]:
   for i in range(N):
    u=i/(N-1); thick=5*naca*chord*(.2969*np.sqrt(max(u,0))-.1260*u-.3516*u*u+.2843*u**3-.1015*u**4)
    V.append([xf+u*chord,y,z+side*thick])
 rows=2*N
 for j in range(len(strips)-1):
  for offset in (0,N):
   for i in range(N-1):
    a=j*rows+offset+i;b=a+1;c=(j+1)*rows+offset+i;d=c+1
    if offset==0:F.extend([[a,c,b],[b,c,d]])
    else:F.extend([[a,b,c],[b,d,c]])
 for j in range(len(strips)-1):
  for i in [0,N-1]:
   a=j*rows+i; b=(j+1)*rows+i;c=j*rows+N+i;d=(j+1)*rows+N+i
   F.extend([[a,b,c],[b,d,c]])
 for j in [0,len(strips)-1]:
  for i in range(N-1):
   a=j*rows+i; b=a+1;c=j*rows+N+i;d=c+1
   F.extend([[a,b,c],[b,d,c]])
 return add(name,trimesh.Trimesh(vertices=V,faces=F,process=False),color)
def finmesh(name,profile,halfwidth,color='white'):
 # (x,z) polygon, with y +- halfwidth
 v=[[x,y,z] for y in [-halfwidth,halfwidth] for x,z in profile];n=len(profile);f=[]
 for i in range(1,n-1):f.extend([[0,i+1,i],[n,n+i,n+i+1]])
 for i in range(n):j=(i+1)%n;f.extend([[i,j,i+n],[j,j+n,i+n]])
 return add(name,trimesh.Trimesh(vertices=v,faces=f,process=False),color)
# aircraft: X front-positive, Y right wing-positive, Z up, approximate C172 planform meters
# CG x=0; nose +3.25, tail -5; wings +/-5.5 m, high at 1.52
loft('Fuselage • sculpted aluminium shell',[
(-4.35,0,.24,.10,.12),(-3.65,0,.18,.24,.25),(-2.8,0,.15,.35,.36),(-1.95,0,.12,.50,.48),(-1.0,0,.06,.65,.63),(.15,0,.04,.72,.74),(1.15,0,.06,.73,.76),(1.95,0,.03,.64,.68),(2.50,0,-.02,.50,.49),(3.03,0,-.02,.35,.34),(3.35,0,.03,.20,.23),(3.52,0,.02,.055,.07)],'white',48)
# cockpit roof, windscreen, and side glazing
box('Cabin roof • removable panel',(.25,0,.82),(2.65,1.42,.16),'white')
for sign,suffix in [(-1,'left'),(1,'right')]:
 y=sign*.681
 # distinct tinted glass window shapes
 box('Front side window '+suffix,(.89,y,.42),(1.00,.018,.55),'glass')
 box('Rear side window '+suffix,(-.23,y,.43),(.79,.018,.51),'glass')
 box('Cabin door • '+suffix,(.91,sign*.723,-.12),(1.10,.026,.72),'cream')
 beam('Door diagonal seam '+suffix,[.36,y,-.4],[.36,y,.71],.012,'dark')
 beam('Door handle '+suffix,[1.06,sign*.753,-.24],[1.24,sign*.753,-.24],.022,'metal')
 beam('Window pillar '+suffix,[.38,y,.0],[.38,y,.78],.03,'white')
 beam('Window aft pillar '+suffix,[-.70,y,.06],[-.70,y,.8],.03,'white')
 beam('Wing strut • '+suffix,[.68,sign*.65,-.12],[.05,sign*3.09,1.29],.062,'metal')
 beam('Strut rear brace • '+suffix,[.55,sign*.7,-.12],[-.1,sign*2.70,1.33],.020,'metal')
 # wing sections and separate ailerons/flaps
 wingmesh('Main high wing • '+suffix,[(sign*.02,1.88,-.62,1.46,0),(sign*2.65,1.74,-.57,1.51,0),(sign*5.40,1.36,-.28,1.72,0)],'white')
 wingmesh('Flap • '+suffix,[(sign*.87,-.42,-.78,1.45,0),(sign*2.87,-.41,-.70,1.52,0)],'cream',.075)
 wingmesh('Aileron • '+suffix,[(sign*2.90,-.37,-.69,1.54,0),(sign*5.16,-.20,-.39,1.71,0)],'cream',.075)
 # wingtip navigation lenses
 uvball('Wingtip navigation light • '+suffix,[1.40,sign*5.40,1.71],[.075,.055,.04], 'red' if sign==-1 else 'orange')
 # horizontal stab and elevator
 wingmesh('Horizontal stabilizer • '+suffix,[(sign*.08,-3.33,-4.40,.34,0),(sign*1.67,-3.55,-4.51,.42,0)],'white',.09)
 wingmesh('Elevator • '+suffix,[(sign*.10,-4.37,-4.77,.34,0),(sign*1.57,-4.47,-4.78,.42,0)],'cream',.07)
 # fixed main landing gear and fairing
 beam('Main landing gear spring • '+suffix,[.08,sign*.55,-.43],[-.04,sign*1.26,-1.33],.063,'metal')
 beam('Axle • '+suffix,[-.04,sign*1.19,-1.33],[-.04,sign*1.41,-1.33],.058,'metal')
 m=trimesh.creation.cylinder(radius=.30,height=.16,sections=32); m.apply_transform(trimesh.geometry.align_vectors([0,0,1],[0,1,0]));m.apply_translation([-.04,sign*1.36,-1.38]);add('Main wheel '+suffix,m,'rubber')
 for yy in [sign*1.46]:ring('Main wheel hub '+suffix,[-.04,yy,-1.38],[0,1,0],.13,.04,'metal')
 # accent long stripe
 beam('Burgundy fuselage stripe '+suffix,[2.52,sign*.48,.12],[-3.31,sign*.27,.12],.023,'red')
 beam('Navy lower stripe '+suffix,[2.52,sign*.48,.05],[-3.3,sign*.27,.05],.014,'blue')
# tail vertical, separate rudder
finmesh('Vertical stabilizer',[(-2.72,.32),(-3.2,1.35),(-3.79,1.86),(-4.15,1.83),(-4.30,.33)],.105,'white')
finmesh('Rudder • hinged',[(-4.15,1.80),(-4.50,1.70),(-4.76,.28),(-4.38,.28)],.075,'cream')
beam('Tail cap red stripe',[-3.84,0,1.79],[-4.15,0,1.78],.035,'red')
# nose wheel
beam('Nose gear • oleo',[2.70,0,-.33],[2.83,0,-1.19],.082,'metal')
beam('Nose gear fork',[2.83,-.14,-1.14],[2.83,.14,-1.14],.034,'metal')
m=trimesh.creation.cylinder(radius=.23,height=.14,sections=28);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],[0,1,0]));m.apply_translation([2.82,0,-1.20]);add('Nose wheel',m,'rubber')
# engine cowling + cooling intakes, spinner, propeller
uvball('Engine cowling', [3.02,0,.03],[.51,.38,.34],'white',3)
uvball('Propeller spinner',[3.60,0,.045],[.24,.15,.15],'metal',3)
for i in range(2):
 ang=i*math.pi
 # vertical prop facing toward nose (disk in YZ-plane)
 p=np.array([3.69,math.sin(ang)*.13,math.cos(ang)*.13]);q=np.array([3.68,math.sin(ang)*1.13,math.cos(ang)*1.13])
 beam('Propeller blade '+str(i+1),p,q,.072,'dark')
 uvball('Propeller tip '+str(i+1),q,[.025,.11,.11],'light')
for side in [-1,1]:uvball('Cowling inlet '+str(side),[3.34,side*.21,.18],[.026,.08,.055],'dark')
# cockpit internals: visible through windshield, fully separable
box('Instrument panel', (1.50,0,.19),(.16,1.16,.62),'instrument')
box('Instrument brow', (1.59,0,.56),(.35,1.20,.08),'dark')
# 2 pilot seats
for side,label in [(-1,'Pilot'),(1,'Copilot')]:
 y=side*.37
 box(label+' seat cushion',[.38,y,-.35],[.72,.48,.16],'seat')
 box(label+' seatback',[-.03,y,-.06],[.17,.51,.68],'seat')
 beam(label+' seat rail',[-.28,y-.17,-.50],[.77,y-.17,-.50],.024,'metal')
 beam(label+' opposite seat rail',[-.28,y+.17,-.50],[.77,y+.17,-.50],.024,'metal')
 # yoke
 beam(label+' control column',[1.34,y,.05],[1.05,y,-.01],.038,'metal')
 box(label+' yoke hub',[1.02,y,-.01],[.11,.16,.11],'dark')
 beam(label+' yoke crossbar',[1.04,y-.19,.04],[1.04,y+.19,.04],.034,'dark')
 beam(label+' yoke left grip',[1.04,y-.19,-.11],[1.04,y-.19,.18],.030,'dark')
 beam(label+' yoke right grip',[1.04,y+.19,-.11],[1.04,y+.19,.18],.030,'dark')
 # six analog gauges with separately colored dial and needle
 for j,(dx,dz) in enumerate([(0,.37),(.23,.37),(-.23,.37),(0,.07),(.23,.07),(-.23,.07)]):
  yy=y+dx
  if abs(yy)>.57:continue
  ring(label+' gauge bezel '+str(j),[1.593,yy,.20+dz-.19],[1,0,0],.099,.083,'metal')
  # dial face oriented along x
  m=trimesh.creation.cylinder(radius=.082,height=.008,sections=28);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],[1,0,0]));m.apply_translation([1.603,yy,.20+dz-.19]);add(label+' gauge dial '+str(j),m,'instrument')
  beam(label+' needle '+str(j),[1.614,yy,.20+dz-.19],[1.615,yy+.045,.20+dz-.16],.005,'light',6)
# center radio stack
for k in range(4):
 box('Radio and avionics stack '+str(k),[1.618,0,.39-k*.124],[.028,.27,.10],'dark')
 box('Radio LCD '+str(k),[1.638,0,.39-k*.124],[.009,.15,.034],'blue')
 for side in [-1,1]:uvball('Radio knob '+str(k)+str(side),[1.65,side*.116,.39-k*.124],[.015,.02,.02],'metal',1)
# mixture/throttle controls
for side,col,label in [(-1,'dark','Throttle'),(1,'red','Mixture')]:
 beam(label+' pushrod',[1.65,side*.24,-.10],[1.38,side*.24,-.12],.024,'metal')
 uvball(label+' knob',[1.72,side*.24,-.10],[.09,.08,.08],col,2)
# front glazing separate clear planar panes
for side in [-1,1]:
 # angled windshield glazed areas approximated as thin skew quadrilaterals
 pts=np.array([[1.47,0,.77],[1.47,side*.66,.77],[2.01,side*.55,.10],[2.01,0,.10]])
 v=np.concatenate([pts,pts+np.array([.012,0,0])]);f=[]
 for i in range(4):j=(i+1)%4;f.extend([[i,j,j+4],[i,j+4,i+4]])
 add('Curved windshield segment '+str(side),trimesh.Trimesh(vertices=v,faces=f,process=False),'glass')
# ribbed cabin floor
box('Cockpit floor',[.32,0,-.55],[2.55,1.05,.07],'dark')
for i in range(8):beam('Cabin floor rib '+str(i),[-.85+i*.31,-.48,-.51],[-.85+i*.31,.48,-.51],.006,'metal',8)
# structural door frame tubes
for sy in [-1,1]:
 for xx in [-.67,.35,1.46]:beam('Cabin frame '+str(sy)+' '+str(xx),[xx,sy*.685,-.51],[xx,sy*.685,.80],.019,'white')
# wing root lower belly red accent
for sy in [-1,1]:
 beam('Tail stripe accent '+str(sy),[-3.55,sy*.24,.44],[-4.08,sy*.11,1.56],.025,'red')
# export and report
os.makedirs('/mnt/data/Cessna172_Editable',exist_ok=True)
path='/mnt/data/Cessna172_Editable/Cessna_172_Editable.glb'
S.export(path)
print('model',path,'parts',len(S.geometry),'vertices',sum(len(g.vertices) for g in S.geometry.values()),'faces',sum(len(g.faces) for g in S.geometry.values()),'bytes',os.path.getsize(path))
