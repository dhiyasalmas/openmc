from mpi4py import MPI
import glob
import os
import time
import openmc

print("Core 2")

start = time.time()
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

openmc.config["cross_sections"]='/home/dhiya/openmclib/endfb-viii.0-hdf5/cross_sections.xml'

# Create plutonium metal material
Pu_metal_sphere = openmc.Material()
Pu_metal_sphere.add_nuclide("Pu239", 3.7047E-2)
Pu_metal_sphere.add_nuclide("Pu240", 1.7512E-3)
Pu_metal_sphere.add_nuclide("Pu241", 1.1674E-3)
Pu_metal_sphere.add_element("Ga", 1.3752E-3)
Spherical_nickel_coating = openmc.Material()
Spherical_nickel_coating.add_element("Ni", 9.3122E-2)
materials = openmc.Materials([Pu_metal_sphere, Spherical_nickel_coating])
materials.export_to_xml()

# Create a single cell filled with the Pu metal
Pu_sphere = openmc.Sphere(r=6.3849, boundary_type='vacuum')
fuel = openmc.Cell(fill=Pu_metal_sphere, region=-Pu_sphere)

Nickel_coating = openmc.Sphere(r=6.3976)
coating = openmc.Cell(fill=Spherical_nickel_coating, region=-Nickel_coating)

geom = openmc.Geometry([fuel, coating])
geom.export_to_xml()

# Finally, define some run settings
settings = openmc.Settings()
settings.batches = 200
settings.inactive = 10
settings.particles = 10000
settings.export_to_xml()

# Run the simulation
#openmc.run(mpi_args=['mpiexec', '-n', '4'])
openmc.run()

#if rank ==0:
#	openmc.StatePoint('statepoint.10.h5')

if rank == 0:
	files = sorted(glob.glob('statepoint.*.h5'))
	if not files:
		raise RuntimeError("Tidak ada statepoint")
	filename = files[-1]
	while not os.path.exists(filename):
		time.sleep(0.1)
else:
	filename = None

filename = comm.bcast(filename, root=0)
comm.Barrier()

if rank==0:
	print(f"Rank 0 berhasil membaca: {filename}")
	sp = openmc.StatePoint(filename)

print("Waktu : ", time.time()-start)
