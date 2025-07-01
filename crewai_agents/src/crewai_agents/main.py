import sys
from datetime import datetime
from .crew import AICouncilCrew

def run(topic: str = "AI governance framework"):
    """Execute the full council evaluation workflow"""
    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year)
    }
    
    try:
        crew = AICouncilCrew().crew()
        result = crew.kickoff(inputs=inputs)
        
        print("\n=== Workflow Results ===")
        print(f"Final Outputs:")
        for task_name, output_path in result.outputs.items():
            print(f"- {task_name}: {output_path}")
        
        return True
    except Exception as e:
        print(f"\nError in workflow execution: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        topic = "AI governance framework"
    
    success = run(topic)
    sys.exit(0 if success else 1)

# from .processing_flow import ProcessingFlow
# from crewai_agents.crew import CrewaiAgents

# def main():
#     print("Starting AI Processing Workflow...")
#     workflow = ProcessingFlow()
    
#     while True:
#         user_input = input("\nEnter your input (or 'quit' to exit): ")
#         if user_input.lower() == 'quit':
#             break
        
#         print("\nProcessing your request...")
#         result = workflow.execute(user_input)
        
#         print("\nFinal Result:")
#         print(result)
#         print("\nProcessing complete!")

# if __name__ == "__main__":
#     main()


# import sys
# import warnings

# from datetime import datetime

# from crewai_agents.crew import CrewaiAgents

# warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


# def run():
#     """
#     Run the crew.
#     """
#     inputs = {
#         'topic': 'AI LLMs',
#         'current_year': str(datetime.now().year)
#     }
    
#     try:
#         CrewaiAgents().crew().kickoff(inputs=inputs)
#     except Exception as e:
#         raise Exception(f"An error occurred while running the crew: {e}")


# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         'current_year': str(datetime.now().year)
#     }
#     try:
#         CrewaiAgents().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         CrewaiAgents().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         "current_year": str(datetime.now().year)
#     }
    
#     try:
#         CrewaiAgents().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")
