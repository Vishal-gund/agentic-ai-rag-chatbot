import java.util.*;
class Employee{
	int id;
	String name;
	int sal;
	
	Employee(int id,String name,int sal){
		this.id = id;
		this.name = name;
		this.sal = sal;
	}
	
	public void setId(int id){
		this.id = id;
	}
	
	public int getId(){
		return id;
	}
	
	public void setName(String name){
		this.name = name;
	}
	
	public String getName(){
		return name;
	}
	
	public void setSal(int sal){
		this.sal = sal;
	}
	
	public int getSal(){
		return sal;
	}
}
class SearchById implements Comparator <Employee>{
	public int compare(Employee emp1 ,Employee emp2){
		
		if(emp1.getId() < emp2.getId()){
			return -1;
		}
		else if(emp1.getId() > emp2.getId()){
			return 1;
		}
		else{
			return 0;
		}
	}
}
class SearchBySal implements Comparator <Employee>{
	public int compare(Employee emp1,Employee emp2){
		
		if(emp1.getSal() < emp2.getSal()){
			return 1;
		}
		else if(emp1.getSal()> emp2.getSal()){
			return -1;
		}
		else{
			return 0;
		}
	}
}

class SortByNAMe implements Comparator<Employee>{
	private boolean ascDesc;
	public SortByNAMe(boolean ascDesc){
		this.ascDesc = ascDesc;
	}
	
	public int compare(Employee emp1,Employee emp2){
		int result = emp1.getName().compareTo(emp2.getName());
		
		return ascDesc ? result:-result;
	}
}
public class EmployeeAppComparator{
	public static void main(String args[]){
		List <Employee> list = new ArrayList<>(); //  List<Employee> list = new ArrayList<>();
		list.add(new Employee(1,"Vishal",10000));
		list.add(new Employee(4,"sham",15000));
		list.add(new Employee(2,"Ankit",5000));
		list.add(new Employee(5,"Ram",7000));
		list.add(new Employee(3,"rajesh",3000));
		
		System.out.println("Origenal data ");
		System.out.printf("%-8s %-15s %-5s \n","Id","Name","Salary");
		System.out.println();
		for(Employee emp : list){
			
			System.out.printf("%-8d %-15s %-5d \n",emp.getId(),emp.getName(),emp.getSal());
		}
		SearchById empSid = new SearchById();
		Collections.sort(list,empSid);
		
		System.out.println("____________________________________");
		System.out.println("Sort by id");
		System.out.printf("%-8s %-15s %-5s \n","Id","Name","Salary");
		System.out.println();
		
		for(Employee emp:list){
			System.out.printf("%-8d %-15s %-5d \n",emp.getId(),emp.getName(),emp.getSal());
		}
		System.out.println("____________________________________");
		System.out.println("Sort by sal");
		System.out.printf("%-8s %-15s %-5s \n","Id","Name","Salary");
		System.out.println();
		
		SearchBySal searchSal = new SearchBySal();
		Collections.sort(list,searchSal);
		for(Employee emp:list){
			System.out.printf("%-8d %-15s %-5d \n",emp.getId(),emp.getName(),emp.getSal());
		}
		System.out.println("____________________________________");
		System.out.println("Sort by name");
		System.out.printf("%-8s %-15s %-5s \n","Id","Name","Salary");
		System.out.println();
		
		//SortByNAMe name = new SortByNAMe();
		Collections.sort(list,new SortByNAMe(true));
		for(Employee emp:list){
			System.out.printf("%-8d %-15s %-5d \n",emp.getId(),emp.getName(),emp.getSal());
		}
		
		
	}
}
