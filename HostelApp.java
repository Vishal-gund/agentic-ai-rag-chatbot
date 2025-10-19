//Create a class HostelStudent with:
//Fields: rollNo, name, roomType (Single, Double, or Dorm), and fees.
//Constructor assigns the fees as  Single = ₹12000  Double = ₹8000//Dorm = ₹5000

// check just for fetch property
import java.util.Scanner;
class HostelStudent{
	int rollNo ;
	String name;
	String roomType;
	int fees;
	HostelStudent(int rollNo,String name,String roomType,int fees){
		this.rollNo = rollNo;
		this.name = name;
		this.roomType = roomType;
		this.fees = fees;
	}
	int getFees(){
		return fees;
	}
	void display(){
		System.out.printf("%-5d  %-10s  %-10S %-5d \n",rollNo,name,roomType,fees);
	}
}


public class HostelApp{
	public static void main(String x[]){
		Scanner sc = new Scanner(System.in);
		
		HostelStudent hs [] = new HostelStudent [6];
		System.out.println("Enter Student RollNum Name RoomType ");
			int s=0;
			int dob=0;
			int dm=0;
		for(int i=0;i<hs.length;i++){
			int rollNo = sc.nextInt();
			sc.nextLine();
			String name = sc.nextLine();
			String roomType = sc.nextLine();
			
			int fees =0;
			
			if(roomType.equals("Single")){
				fees = 1200;
				s++;
			}
			else if(roomType.equals("Double")){
				fees = 8000;
				dm++;
			}
			else if(roomType.equals("Dorm")){
				fees = 5000;
				dob++;
			}
			else{
				System.out.println("Invalid room type for student rollNo: ");
			}
			
			hs[i] = new HostelStudent (rollNo,name,roomType,fees);
		}
		int totalRev =0;
		System.out.printf("%-5s %-10s %-10s %-5s \n","RollNum","Name","RoomType","Fees");
		for(int i=0;i<hs.length;i++){
			hs[i].display();
			
			totalRev+=hs[i].getFees();
		}
		System.out.println("students are assigned to each room type");
		System.out.println("Single Romm = "+s);
		System.out.println("Double Romm = "+dm);
		System.out.println("Dorm Romm = "+dob);
		
		System.out.println("Total Revenue = " + totalRev);
	}
}