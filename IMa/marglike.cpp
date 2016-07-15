/*IMa2p 2009-2015 Jody Hey, Rasmus Nielsen, Sang Chul Choi, Vitor Sousa, Janeen Pisciotta, and Arun Sethuraman */
#undef GLOBVARS
#include "imamp.hpp"
/* calculate marginal likelihood */


/*
implement thermodynamic integration over a large number of intervals

we want the marginal likelihood under the model

p(D) 

for p_Bi(D|G)

where Bi is a heating value i,  for a total of  j values   0<i<j-1

Let L_i  be the mean of p_Bi(D|G) sampled over the course of the run

L_i = Sum[p_Bi(D|G)]/k    for k samples

Then 

p(d) = Sum[ (Bi-B(i-1)) (L_i + L_(i-1))/2, {i, 1, j-1}] 

this is trapezoidal rule 

Also record the harmonic mean  - have to use eexp()

p(d) = 1/ [ SUM[ 1/(p(D|G)]/k ]

*/
#define LOG_10_2  0.30102999566398119521
#define OCUTOFF  10

//double thermosum[MAXCHAINS]; 



void initmarginlikecalc()
{
  int i;
  //harmonicsum = 0.0;
 // harmonicsum_eexp = 0.0;
  for (i=0;i<numprocesses * numchains;i++)
    thermosum[i]  = 0.0;
}

/* harmonic mean calculations,  has to deal with using eexp() */
//AS: Mon Nov 30 17:13:29 EST 2015
//need to pass currentid to this function
void summarginlikecalc(int currentid)
{
  int i;
  int nchains = numchains;
  /*  10/6/2011  commented out some old code for calculation harmonic mean   
    this was moved to harmonicmarginlikecalc() 
  static int ei = 0;
  int tempz;
  int i, zadj;
  double tempm;

  //harmonicsum += 1.0/exp(C[0]->allpcalc.pdg); simple form has floating point problems
  eexp(C[0]->allpcalc.pdg,&tempm,&tempz);
  if (ei < HARMONICMEANCHECK)
  {
    harmonicsump[ei].m = 1.0/tempm;
    harmonicsump[ei].z = -tempz;
    if (harmonicsump[ei].z > maxz)
      maxz = harmonicsump[ei].z;
  }
  else
  {
    if (ei == HARMONICMEANCHECK)
    {
      for (i = 0; i < ei; i++)
      {
        zadj = harmonicsump[i].z - (maxz - OCUTOFF);
        harmonicsum_eexp += harmonicsump[i].m * pow (10.0, (double) zadj);
      }
    }
    zadj = -tempz - (maxz - OCUTOFF);
    harmonicsum_eexp += (1.0/tempm) * pow (10.0, (double) zadj);
  }
  ei++; */
//AS: Mon Nov 30 16:57:08 EST 2015
// thermosum[] has to be computed across chains across processors
// so has to be collated, and not just computed like this. 
//   std::cout << "Thermosums on processor " << currentid << "\n";
//
//  if (currentid == (numprocesses -1) && ODD(numprocesses * numchains)==0)
//	nchains-=1;

//AS: realized that the C[i]->allpcalc.pdg, or likelihood values should also be swapped
//according to beta values, if the chains have swapped.
//Since beta values are moving around, I have to check back and index them according to allbetas
/*#ifdef MPI_ENABLED
	for (int x = 1; x < numprocesses; x++) {
		for (i = 0; i < numchains; i++) {
			if (beta[i] != allbetas[currentid * numchains + i]) { //AS: here betas have been swapped out
				MPI::COMM_WORLD.Send(&C[i]->allpcalc.pdg, 1, MPI::DOUBLE, 0, 9898);
			}
			




#endif
*/

  for (i=0 ;i< nchains;i++){
//	std::cout << "Processor " << currentid << " C[i]->allpcalc.pdg " << C[i]->allpcalc.pdg << " i = " << i << "\n";
    thermosum[i] = thermosum[i] + C[i]->allpcalc.pdg;
	//if (thermosum[i] < -1e8)
	//	thermosum[i] = -1e8;
  //std::cout << "Processor " << currentid << "beta " << beta[i] << " i= " << i << "\n";
  //std::cout << "thermosum[i] = " << thermosum[i] << "\n";
  }
    /*
  //AS: to collate thermosum across processors
  #ifdef MPI_ENABLED
	for (int x = 1; x < numprocesses; x++) {
	//	if (currentid == numprocesses - 1)			
		if (currentid == x) {
			for (int v = 0; v < numchains; v++) {
				MPI::COMM_WORLD.Send(&thermosum[v], 1, MPI::DOUBLE, 0, 9898);
			}
		}
		if (currentid == 0) {
			int nchains = numchains;
			//if (x == (numprocesses - 1) && ODD(numprocesses * numchains)==0)
			//	numchains-=1;
			for (int v = 0; v < numchains; v++) {
				MPI::COMM_WORLD.Recv(&thermosum[x * nchains + v], 1, MPI::DOUBLE, x, 9898);
			}
		}
	}
	//if (currentid == 0) {
	//	std::cout << "Thermosums:\n";
	//	for (int x =0; x < numprocesses * numchains; x++)
	//		std::cout << thermosum[x] << "\t";
	//		std::cout << "\n";
	//}
  #endif 
*/



  /*if (currentid !=0 && numprocesses > 1) {
	try {
		int tempcurrentid = currentid;
		request[0] = MPI::COMM_WORLD.Isend(&tempcurrentid, 1, MPI::INT, 0, 9898);
	} catch (MPI::Exception e) {
		std::cout << "Error in sending my id!\n";
		MPI::COMM_WORLD.Abort(-1);
	}
	try {
		MPI::Request::Waitall(1, &request[0]);
	} catch (MPI::Exception e) {
		std::cout << e.Get_error_string() << e.Get_error_code() << "\n";
		std::cout << "Error in sending my id!\n";
		MPI::COMM_WORLD.Abort(-1);
	}
	for (int v = currentid * numchains ; v < numchains; v++) {
		try {
			request[0] = MPI::COMM_WORLD.Isend(&thermosum[v], 1, MPI::DOUBLE, 0, v * 9999);
		} catch (MPI::Exception e) {
			std::cout << e.Get_error_string() << e.Get_error_code() << "\n";
			std::cout << "Error in sending thermosum!\n";
			MPI::COMM_WORLD.Abort(-1);
			return;
		}
		
		try {
			MPI::Request::Waitall(1, &request[0]);
		} catch (MPI::Exception e) {
			std::cout << e.Get_error_string() << e.Get_error_code() << "\n";
			std::cout << "Error in sending my id!\n";
			MPI::COMM_WORLD.Abort(-1);
			return;
		}
	}
	} else if (currentid == 0 && numprocesses > 1) {
	int tempcurrentid = 0;
	try {
		request[0] = MPI::COMM_WORLD.Irecv(&tempcurrentid, 1, MPI::INT, MPI_ANY_SOURCE, 9898);
	} catch (MPI::Exception e) {
		std::cout << "Error in receiving the other processors's ID!\n";
		MPI::COMM_WORLD.Abort(-1);
	}
	try {
		MPI::Request::Waitall(1, &request[0]);
	} catch (MPI::Exception e) {
		std::cout << e.Get_error_string() << e.Get_error_code() << "\n";
		MPI::COMM_WORLD.Abort(-1);
	}
	for (int v = tempcurrentid * numchains; v < numchains; v++) {
		try {
			request[0] = MPI::COMM_WORLD.Irecv(&thermosum[v], 1, MPI::DOUBLE, tempcurrentid, v * 9999);
		} catch (MPI::Exception e) {
			std::cout << e.Get_error_string() << e.Get_error_code() << "\n";
			std::cout << "Error in receiving thermosum array!\n";
			MPI::COMM_WORLD.Abort(-1);
			return;
		}
		try {
			MPI::Request::Waitall(1, &request[0]);
		} catch (MPI::Exception e) {
			std::cout << e.Get_error_strnig() << e.Get_error_code() << "\n";
			MPI::COMM_WORLD.Abort(-1);
			return;
		}
	}

	} //AS: closes else if*/
 
}

double harmonicmarginlikecalc(int k)
{
  double hmlog;
  int gi, zadj;
  int pdgp;
  int tempz;
  double tempm;
  struct extendnum *harmonicsump;
  int maxz = 0;
  double  harmonicsum_eexp = 0.0;

  harmonicsump = (struct extendnum *) malloc ((size_t) ((genealogiessaved + 1) * sizeof (struct extendnum)));

  pdgp = 4*numpopsizeparams + 3* nummigrateparams;  // position in gsampinf[gi] that holds pdg
  for (gi = 0; gi < genealogiessaved; gi++)
  {
    eexp(gsampinf[gi][pdgp],&tempm,&tempz);
    harmonicsump[gi].m = 1.0/tempm;
    harmonicsump[gi].z = -tempz;
    if (harmonicsump[gi].z > maxz)
      maxz = harmonicsump[gi].z;
  }
  for (gi = 0; gi < genealogiessaved; gi++)
  {
    zadj = harmonicsump[gi].z - (maxz - OCUTOFF);
    harmonicsum_eexp += harmonicsump[gi].m * pow (10.0, (double) zadj);
  }
  hmlog = -(log (harmonicsum_eexp) - log( (double) genealogiessaved) + (maxz - OCUTOFF) * LOG10);
  XFREE(harmonicsump);
  return hmlog;
}
/* made this change based on audes recommendation 9/16/2011 */ 
// AS: Mon Nov 30 17:05:30 EST 2015
// Looks like this calculation should be fine - isn't affected as long as thermosum is "collated"

double thermomarginlikecalc(int k)
{
  int i;
  double width, sum; 
  double mcalc = 0.0;
  /* trapezoid rule */
  /*for (i= (numprocesses * numchains - 2); i>= 0;i--)
  {
    if (allbetas[i+1]==0.0)
      mcalc += (allbetas[i+1]- allbetas[i]) * (thermosum[i]/k);
    mcalc += (allbetas[i+1]- allbetas[i]) * ((thermosum[i]/k + thermosum[i+1]/k)/2);
  }*/
  
  /* Simpson's rule  - must ensure previously that the number of intervals is even*/
  /* so the number of chains must  be odd.
    but since we are counting from zero,  the value of numchains must  even */
  //AS: debug only
  //std::cout << "Thermosums\n";
  //for (i = 0; i <= numprocesses * numchains -1; i++)
  //std::cout << thermosum[i] << "\t";
  //std::cout << "numchains is " << numchains << "\n";
  
  width = 1.0/ (float) (numprocesses * numchains -1);
  //std::cout << "width is " << width << "\n";
  sum = 0.0;
  for (i = 0;i<=numprocesses * numchains-1;i+=2)
  {
    if (i != (numprocesses * numchains - 1))  // for chain[numchains-1] use a value of 0.0 because under thermodynamic integration the mean likelihood at Beta=0 is 0.0 
      sum += 4.0 * (thermosum[i]/k);
  }
  for (i = 1;i<=numprocesses * numchains-2;i+=2)
  {
    sum += 2.0 * (thermosum[i]/k);
  }
  mcalc = width * sum/3.0; 
  //std::cout << "sum here is " << sum << "\n";
  //std::cout << "k here is " << k << "\n";
  //std::cout << "mcalc is " << mcalc << "\n";
  return mcalc;
}


