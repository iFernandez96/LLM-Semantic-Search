# Pros and Cons of LLM vs Structured Rule Based Query System

## LLM

### Pros
- Handles complex quieries
- Handles variant phrasing
- Learns dynamically from context
    - May introduce hallucinations the deeper the context
- Supports fuzzy matching

### Cons
- May produce hallucinated results
    - May end up spending a lot of time corraling the LLM without anything to show for it 
- Requires cloud-based LLM access   
    - Not necessarily true. We can run locally: [Dave's Garage LLM video](https://www.youtube.com/watch?v=mUGsv_IHT-g)
- May require strong hardware and large storage


## Structured Ruled Based Query System

### Pros
- Deterministic and accurate
    - Accuracy is determined by how well the Ruled Based System works
    - Does not hallucinate
- Runs locally without cloud APIs.
    - Requires less compute than LLM by a longshot.
- Fast execution
- Can run on pretty much any computer
- Small footprint
    - Does not take much storage


### Cons
- Requires manual schema updates
    - Harder to maintain
    - Harder to adapt to new scenarios
    - Requires more manual labor than LLM
- Can't handle sentence structure variations
    - May be able to handle some, but not as good as LLM.
- May take more time to setup than LLM



## Hybrid

### Pros
-  
