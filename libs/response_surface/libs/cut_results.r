cut_results <- function(x, limits) {
	nlimits = length(limits)
	odata = x
	odata[] = nlimits+1
	for (i in nlimits:1) odata[x<=limits[i]]=i
	odata[is.na(x)]=NaN
	return(odata)
}
