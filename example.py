"""Example script demonstrating English abstract move recognition."""

import os
from semantic_toolkit.move_recognition import analyze_english_abstract

# Example abstract (from the plan documentation)
abstract = """
This study addresses the growing need for efficient data processing.
We aim to develop a novel algorithm for large-scale data analysis.
The proposed method combines deep learning with traditional statistical approaches.
Results show a 40% improvement in processing speed.
These findings suggest significant potential for real-world applications.
"""

def main():
    """Run the example analysis."""
    print("=" * 60)
    print("English Abstract Move Recognition Example")
    print("=" * 60)
    print()

    # Check if API key is set
    if not os.getenv("ZHIPU_API_KEY"):
        print("Warning: ZHIPU_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment to run this example.")
        return

    try:
        print("Analyzing abstract...")
        print()

        result = analyze_english_abstract(abstract)

        # Print summary
        print("Summary:")
        print(f"  Total sentences: {result.summary['total_sentences']}")
        print()
        print("Move counts:")
        for move_type, count in result.summary['move_counts'].items():
            if count > 0:
                print(f"  {move_type}: {count}")
        print()

        # Print individual sentences
        print("Detailed Analysis:")
        print("-" * 60)
        for sentence in result.sentences:
            print(f"{sentence.move_type.value:12} | confidence: {sentence.confidence:.2f}")
            print(f"             | {sentence.text}")
            print()

        print("=" * 60)
        print("Analysis complete!")
        print("=" * 60)

    except Exception as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    main()
