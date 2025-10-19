
import java.util.*;
class Employee{
	private int id;
	private String name;
	private String designation;
	private int salary;
	private int exp;
	
	public Employee(int id,String name,String designation,int salary,int exp){
		this.id = id;
		this.name = name;
		this.designation = designation;
		this.salary = salary;
		this.exp = exp;
	}
	
	int getId(){
		return id;
	}
	
	
	String getName(){
		return name;
	}
	
	String getDesignation(){
		return designation;
	}
	
	int getSalary(){
		return salary;
	}
	
	int getExperience(){
		return exp;
	}
	
	void setDesignation(String designation){
		this.designation = designation;
	}
	void setSalary(int salary){
		this.salary = salary;
	}
}


public class EmployeeDetailApp{
	public static void main(String x[]){
		Scanner sc = new Scanner(System.in);
		
		Employee emp [] = new Employee[10];
		System.out.println("Enter a data in array");
		emp[0] = new Employee( 101,"Vishal","Soft Eng",20000,5);
		emp[1] = new Employee( 102,"Sham","Sen Soft Eng",30000,6);
		emp[2] = new Employee( 103,"ram","Doctor",40000,7);
		int count =3;
		
		do{
			System.out.println("__________________________________________________");
			System.out.println("Enter 1 =  Add new employee record");
			System.out.println("Enter 2 = display all employee record ");
			System.out.println("Enter 3 = Search Employee id ");
			System.out.println("Enter 4 =  Update Employee designation and salary");
			System.out.println("Enter 5 =  Delet Employee record by id");
			System.out.println("Enter 6 =  Display Employee record experience more than 5 year");
			System.out.println("Enter 7 =  Display Employee record salary more than 50,000 year");
			System.out.println("Enter 8 =  Display Employee with highest salary");
			System.out.println("Enter 9 =  Display Employee by salary decending order");
			System.out.println("Enter 10 =  Display cont Employee by there designation ");
			System.out.println("__________________________________________________");
			System.out.println("Enter Your choise");
	
			int choice = sc.nextInt();
			
			switch (choice) {
                case 1:
                    if (count >= emp.length) {
                        System.out.println("Employee list is full.");
                        break;
                    }
                    System.out.print("Enter ID: ");
                    int id = sc.nextInt();
                    sc.nextLine(); // consume newline
					
                    System.out.print("Enter Name: ");
                    String name = sc.nextLine();
					
                    System.out.print("Enter Designation: ");
                    String designation = sc.nextLine();
					
                    System.out.print("Enter Salary: ");
                    int salary = sc.nextInt();
					
                    System.out.print("Enter Experience: ");
                    int exp = sc.nextInt();

                    emp[count++] = new Employee(id, name, designation, salary, exp);
                    System.out.println("Employee added successfully.");
                    break;



                case 2:
					
                    System.out.printf("%-5s %-10s %-15s %-10s %-10s\n", "ID", "Name", "Designation", "Salary", "Exp");
                    for (int i = 0; i < count; i++) {
                        if (emp[i] != null) {
                            System.out.printf("%-5d %-10s %-15s %-10d %-10d\n",
                                    emp[i].getId(),
                                    emp[i].getName(),
                                    emp[i].getDesignation(),
                                    emp[i].getSalary(),
                                    emp[i].getExperience());
                        }
                    }
                    break;


					case 3:
						System.out.println("Eneter a search employee id");
						int sId = sc.nextInt();
						for(int i=0;i<count;i++){
							if(emp[i].getId() == sId){
								System.out.printf("%-5d %-10s %-15s %-10d %-10d\n",
                                    emp[i].getId(),
                                    emp[i].getName(),
                                    emp[i].getDesignation(),
                                    emp[i].getSalary(),
                                    emp[i].getExperience());
							}
						}
					break;
					
					case 4:
						System.out.println("Enter a new ID");
						int newId = sc.nextInt();
						sc.nextLine();
						for(int i=0;i<count;i++){
							if( emp[i].getId()==newId){
								String newDesi = sc.nextLine();
								int newSalary = sc.nextInt();
								
								
								emp[i].setDesignation(newDesi); 
								emp[i].setSalary(newSalary);
								
								System.out.println("Employee id upadated successfully");
								
							}
						}
					break;
					
					case 5:
						System.out.println("Enter a delete Id");
						int delId = sc.nextInt();
					for(int i=0;i<count;i++){
						for(int j=i;j<count-1;j++){
							if(emp[i].getId() == delId){
								emp[j] = emp[j + 1];
							}
						}
						emp[count-1] = null;
						count--;
					}
					System.out.println("Id is delete");
					break;
					
					case 6:
						System.out.println("Deetails of those experience more than 5 year");
						for(int i=0;i<count;i++){
							if(emp[i].getExperience() > 5){
								System.out.printf("%-5d %-10s %-15s %-10d %-10d\n",
                                    emp[i].getId(),
                                    emp[i].getName(),
                                    emp[i].getDesignation(),
                                    emp[i].getSalary(),
                                    emp[i].getExperience());
							}
						}
					break;
					case 7:
						System.out.println("Details of employee those salary greater than 50,000 ");
						for(int i=0;i<count;i++){
							if(emp[i].getSalary() > 50000){
								System.out.printf("%-5d %-10s %-15s %-10d %-10d\n",
                                    emp[i].getId(),
                                    emp[i].getName(),
                                    emp[i].getDesignation(),
                                    emp[i].getSalary(),
                                    emp[i].getExperience());
							}
						}
						
					break;
						
					
					
					case 8:
						System.out.println("highest salary of Employee");
						int high =emp[0].getSalary();
						for(int i=0;i<count;i++){
							if(emp[i].getSalary() > high){
								high = emp[i].getSalary();
								System.out.printf("%-5d %-10s %-15s %-10d %-10d\n",
									emp[i].getId(),
                                    emp[i].getName(),
                                    emp[i].getDesignation(),
                                    emp[i].getSalary(),
                                    emp[i].getExperience());
							}
						}
						
					break;
					
					case 9:
						System.out.println("Sort employees by salary in descending order.");
						for(int i=0;i<count;i++){
							for(int j=0;j<count-1;j++){
								if(emp[j].getSalary() < emp[j+1].getSalary()){
									Employee temp = emp[j];
									emp[j] = emp[j+1];
									emp[j+1] = temp;
								}
							}
						}
						for(int i=0;i<count;i++){
							if(emp[i] != null){
								System.out.printf("%-5d %-10s %-15s %-10d %-10d\n",
									emp[i].getId(),
                                    emp[i].getName(),
                                    emp[i].getDesignation(),
                                    emp[i].getSalary(),
                                    emp[i].getExperience());
							}
						}
					break;
					
					case 10:
						System.out.println("Enter the disignation of finding emplyee count");
						sc.nextLine();
						String sDesignation = sc.nextLine();
						
						int countOfEmp = 0;
						
						for(int i=0;i<count;i++){
							if(emp[i] != null && emp[i].getDesignation().equalsIgnoreCase(sDesignation)){
								countOfEmp++;
							}
							
						}
						System.out.println(sDesignation +" count = "+countOfEmp);
							
						
					break;
                case 0:
                    System.out.println("Thank you for using the app.");
                    System.exit(0);
                    break;

                default:
                    System.out.println("Invalid choice! Try again.");
            }
        } while (true);
    }
}