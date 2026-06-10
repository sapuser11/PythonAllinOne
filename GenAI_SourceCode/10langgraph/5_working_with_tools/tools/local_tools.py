from langchain_core.tools import tool
##Add custom tool which can be integrated in the whole scheme of things
##To perform tasks specific to my org / use case
##Rather depending on online tools


##@tool is a decorator (annotations)
##We have to define a doc string to instruct the langgraph framework when to use this tool
##by specifying the input and output types as a doc string
@tool
def my_custom_tool(query: str) -> str:
    """
        This is a custom tool that processes the input string.

        Args:
            query: The input string to process.

        Returns:
            The processed output string.
    """
    # Implement your custom tool logic here
    return f"Processed: {query}"

@tool
def update_vendor_data(vendor_id: str, data: dict) -> str:
    """
        This is a custom tool that updates vendor data.

        Args:
            vendor_id: The ID of the vendor to update.
            data: The new data to update for the vendor.

        Returns:
            A confirmation message indicating the update status.
    """
    # Implement your custom tool logic here
    return f"Updated vendor {vendor_id} with data: {data}"